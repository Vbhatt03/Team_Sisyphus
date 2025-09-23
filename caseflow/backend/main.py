from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import json
import hmac
import base64
import hashlib
import uuid
import shutil
from datetime import datetime, timedelta
import logging

from models import User, Case, ChecklistItem, CaseDiaryPage, create_db_and_tables, get_session
from auth import verify_password, get_password_hash, create_access_token, verify_token
from processors import DocumentProcessor, ComplianceGenerator, CaseDiaryGenerator, ChargesheetGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CaseFlow API", version="1.0.0")

# Health check endpoint to quickly verify the backend is reachable
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

# Simple health check endpoint (useful to verify the backend is up before attempting login)
@app.get("/health")
def health():
    return {"status": "ok"}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175", "http://localhost:5176", "http://127.0.0.1:5176", "http://localhost:5177", "http://127.0.0.1:5177", "http://localhost:5178", "http://127.0.0.1:5178"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
OCR_API_KEY = os.getenv("OCR_SPACE_API_KEY", "K88629238088957")  # Default from config
DIRECT_DOWNLOAD_SECRET = os.getenv("DIRECT_DOWNLOAD_SECRET", "change-this-direct-download-secret")

def _sign_path(case_id: int, rel_path: str, expires_ts: int) -> str:
    msg = f"{case_id}:{rel_path}:{expires_ts}".encode()
    sig = hmac.new(DIRECT_DOWNLOAD_SECRET.encode(), msg, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip('=')

def _verify_signature(case_id: int, rel_path: str, expires_ts: int, signature: str) -> bool:
    if expires_ts < int(datetime.utcnow().timestamp()):
        return False
    expected = _sign_path(case_id, rel_path, expires_ts)
    # Timing safe compare
    return hmac.compare_digest(expected, signature)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# Auth endpoints
@app.post("/api/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username}
    }

@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username}

# Case endpoints
@app.post("/api/cases")
def create_case(
    name: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    case = Case(user_id=current_user.id, name=name)
    session.add(case)
    session.commit()
    session.refresh(case)
    
    # Create directory structure
    case_dir = DATA_DIR / str(case.id)
    (case_dir / "uploads").mkdir(parents=True, exist_ok=True)
    (case_dir / "outputs" / "json").mkdir(parents=True, exist_ok=True)
    
    return {"id": case.id, "name": case.name, "created_at": case.created_at}

@app.get("/api/cases")
def get_cases(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    cases = session.exec(select(Case).where(Case.user_id == current_user.id)).all()
    return [{"id": case.id, "name": case.name, "created_at": case.created_at} for case in cases]

# File upload endpoints
@app.post("/api/upload")
async def upload_file(
    case_id: int = Form(...),
    type: str = Form(...),  # fir, victim_med, accused_med, statement
    skip: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id) / "uploads"
    case_dir.mkdir(parents=True, exist_ok=True)
    
    if skip:
        return {"status": "skipped", "type": type}
    
    if not file:
        raise HTTPException(status_code=400, detail="File is required when not skipping")
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size and file.size > 20 * 1024 * 1024:  # 20MB
        raise HTTPException(status_code=400, detail="File size must be less than 20MB")
    
    # Map type to filename
    filename_map = {
        "fir": "fir.pdf",
        "victim_med": "victim_med.pdf", 
        "accused_med": "accused_med.pdf",
        "statement": "statement.pdf"
    }
    
    if type not in filename_map:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    filename = filename_map[type]
    file_path = case_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "status": "uploaded",
        "type": type,
        "filename": filename,
        "size": file.size
    }

# Processing endpoints
@app.post("/api/parse")
def parse_documents(
    case_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    processor = DocumentProcessor(OCR_API_KEY)
    
    try:
        results = processor.parse_uploaded_pdfs(case_dir)
        return results
    except Exception as e:
        logger.error(f"Parse error for case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

# Compliance endpoints
@app.post("/api/compliance/run")
def run_compliance(
    case_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    generator = ComplianceGenerator(case_dir)
    
    try:
        results = generator.generate_compliance_checklist()
        
        if results["status"] == "success":
            # Clear existing checklist items for this case
            session.exec(select(ChecklistItem).where(ChecklistItem.case_id == case_id)).all()
            existing_items = session.exec(select(ChecklistItem).where(ChecklistItem.case_id == case_id)).all()
            for item in existing_items:
                session.delete(item)
            
            # Add new checklist items
            for item_data in results["checklist_items"]:
                item = ChecklistItem(
                    case_id=case_id,
                    section=item_data["section"],
                    text=item_data["text"],
                    checked=item_data["checked"]
                )
                session.add(item)
            
            session.commit()
        
        return results
    except Exception as e:
        logger.error(f"Compliance generation error for case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Compliance generation failed: {str(e)}")

@app.get("/api/compliance")
def get_compliance(
    case_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    items = session.exec(select(ChecklistItem).where(ChecklistItem.case_id == case_id)).all()
    return [
        {
            "id": item.id,
            "section": item.section,
            "text": item.text,
            "checked": item.checked,
            "updated_at": item.updated_at
        }
        for item in items
    ]

@app.get("/api/compliance/raw")
def get_compliance_markdown(
    case_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Return the raw markdown content of the compliance checklist.

    The existing /api/compliance endpoint only returns parsed checklist items
    (the lines that begin with - [ ] or - [x]). This omits important context
    like the title, victim age note, section headings and grouping labels
    (🚨 To-Do / ✅ Completed). The frontend can call this endpoint to render
    the full markdown while still using /api/compliance for structured item
    interaction (toggling, editing) if desired.
    """
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case_dir = DATA_DIR / str(case_id)
    md_path = case_dir / "outputs" / "compliance" / "compliance_checklist.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Compliance checklist markdown not found")

    try:
        content = md_path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read checklist markdown: {e}")

    return {
        "case_id": case_id,
        "filename": md_path.name,
        "path": str(md_path),
        "content": content
    }

@app.patch("/api/compliance/{item_id}")
def update_compliance_item(
    item_id: int,
    checked: Optional[bool] = None,
    text: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    item = session.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == item.case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if checked is not None:
        item.checked = checked
    if text is not None:
        item.text = text
    
    item.updated_at = datetime.utcnow()
    session.commit()
    
    return {"id": item.id, "checked": item.checked, "text": item.text, "updated_at": item.updated_at}

# Case diary endpoints
@app.post("/api/case-diary/generate")
def generate_case_diary(
    case_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    generator = CaseDiaryGenerator(case_dir)
    
    try:
        results = generator.generate_case_diary()
        
        if results["status"] == "success":
            # Clear existing diary pages for this case
            existing_pages = session.exec(select(CaseDiaryPage).where(CaseDiaryPage.case_id == case_id)).all()
            for page in existing_pages:
                session.delete(page)
            
            # Add new diary pages
            for page_data in results["pages"]:
                page = CaseDiaryPage(
                    case_id=case_id,
                    page_number=page_data["page_number"],
                    content=page_data["content"]
                )
                session.add(page)
            
            session.commit()
        
        return results
    except Exception as e:
        logger.error(f"Case diary generation error for case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Case diary generation failed: {str(e)}")

@app.get("/api/case-diary")
def get_case_diary_page(
    case_id: int = Query(...),
    page_number: int = Query(1),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    page = session.exec(
        select(CaseDiaryPage).where(
            CaseDiaryPage.case_id == case_id,
            CaseDiaryPage.page_number == page_number
        )
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    total_pages = session.exec(
        select(CaseDiaryPage).where(CaseDiaryPage.case_id == case_id)
    ).all()
    
    return {
        "page_number": page.page_number,
        "content": page.content,
        "updated_at": page.updated_at,
        "total_pages": len(total_pages)
    }

@app.put("/api/case-diary")
def save_case_diary_page(
    case_id: int = Form(...),
    page_number: int = Form(...),
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    page = session.exec(
        select(CaseDiaryPage).where(
            CaseDiaryPage.case_id == case_id,
            CaseDiaryPage.page_number == page_number
        )
    ).first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    page.content = content
    page.updated_at = datetime.utcnow()
    session.commit()
    
    return {"status": "saved", "updated_at": page.updated_at}

@app.post("/api/case-diary/next")
def get_next_diary_page(
    case_id: int = Form(...),
    current_page_number: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    next_page = session.exec(
        select(CaseDiaryPage).where(
            CaseDiaryPage.case_id == case_id,
            CaseDiaryPage.page_number == current_page_number + 1
        )
    ).first()
    
    if not next_page:
        raise HTTPException(status_code=404, detail="No next page available")
    
    total_pages = len(session.exec(
        select(CaseDiaryPage).where(CaseDiaryPage.case_id == case_id)
    ).all())
    
    return {
        "page_number": next_page.page_number,
        "content": next_page.content,
        "updated_at": next_page.updated_at,
        "total_pages": total_pages
    }

# Chargesheet endpoints
@app.post("/api/chargesheet/generate")
def generate_chargesheet(
    case_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    generator = ChargesheetGenerator(case_dir)
    
    try:
        results = generator.generate_chargesheet()
        return results
    except Exception as e:
        logger.error(f"Chargesheet generation error for case {case_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chargesheet generation failed: {str(e)}")

# File serving endpoints
@app.get("/api/files")
def list_files(
    case_id: int = Query(...),
    kind: str = Query(...),  # uploads, json, compliance, case_diary, final
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    
    if kind == "uploads":
        files_dir = case_dir / "uploads"
    elif kind == "json":
        files_dir = case_dir / "outputs" / "json"
    elif kind == "compliance":
        files_dir = case_dir / "outputs" / "compliance"
    elif kind == "case_diary":
        files_dir = case_dir / "outputs" / "case_diary"
    elif kind == "final":
        files_dir = case_dir / "outputs" / "final"
    else:
        raise HTTPException(status_code=400, detail="Invalid file kind")
    
    if not files_dir.exists():
        return {"files": []}
    
    files = []
    now_ts = int(datetime.utcnow().timestamp())
    default_ttl = 600  # 10 minutes link validity
    for file_path in files_dir.iterdir():
        if file_path.is_file():
            rel_path = str(file_path.relative_to(case_dir)).replace('\\', '/')
            exp = now_ts + default_ttl
            sig = _sign_path(case_id, rel_path, exp)
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "download_url": f"/api/files/download?case_id={case_id}&path={rel_path}",
                "direct_download_url": f"/api/files/direct?case_id={case_id}&path={rel_path}&exp={exp}&sig={sig}",
                "expires_at": datetime.utcfromtimestamp(exp).isoformat() + 'Z'
            })

    return {"files": files, "link_ttl_seconds": default_ttl}

@app.get("/api/files/download")
def download_file(
    case_id: int = Query(...),
    path: str = Query(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify case ownership
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case_dir = DATA_DIR / str(case_id)
    file_path = case_dir / path
    
    # Security check - ensure path is within case directory
    try:
        file_path.resolve().relative_to(case_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/octet-stream'
    )

@app.post("/api/files/direct-link")
def create_direct_download_link(
    case_id: int = Form(...),
    path: str = Form(...),  # relative path under the case directory (e.g. outputs/final/chargesheet.md)
    ttl_seconds: int = Form(300),  # default 5 minutes
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Create a short-lived signed download URL that does not require the auth header.

    Frontend can POST here with form data and then present the returned URL as a direct
    browser link (useful for right-click save or embedding in anchors)."""
    case = session.exec(select(Case).where(Case.id == case_id, Case.user_id == current_user.id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if ttl_seconds <= 0 or ttl_seconds > 3600:
        raise HTTPException(status_code=400, detail="ttl_seconds must be between 1 and 3600")

    case_dir = DATA_DIR / str(case_id)
    file_path = case_dir / path
    try:
        file_path.resolve().relative_to(case_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    expires_ts = int((datetime.utcnow() + timedelta(seconds=ttl_seconds)).timestamp())
    signature = _sign_path(case_id, path, expires_ts)
    # Provide absolute path param as relative to case root
    return {
        "url": f"/api/files/direct?case_id={case_id}&path={path}&exp={expires_ts}&sig={signature}",
        "expires_at": datetime.utcfromtimestamp(expires_ts).isoformat() + 'Z'
    }

@app.get("/api/files/direct")
def direct_signed_download(
    case_id: int = Query(...),
    path: str = Query(...),
    exp: int = Query(...),
    sig: str = Query(...)
):
    """Serve a file using a signed, time-limited URL without requiring auth header."""
    if not _verify_signature(case_id, path, exp, sig):
        raise HTTPException(status_code=403, detail="Invalid or expired link")

    case_dir = DATA_DIR / str(case_id)
    file_path = case_dir / path
    try:
        file_path.resolve().relative_to(case_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)