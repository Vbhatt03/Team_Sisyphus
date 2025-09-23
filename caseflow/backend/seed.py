import sys
import os
from sqlmodel import Session, create_engine
from models import create_db_and_tables, User, Case
from auth import get_password_hash
import shutil
from pathlib import Path

# Use the same engine as in models.py
DATABASE_URL = "sqlite:///./caseflow.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_demo_user():
    """Create a demo user for testing"""
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if demo user already exists
        from sqlmodel import select
        existing_user = session.exec(select(User).where(User.username == "demo")).first()
        if existing_user:
            print("Demo user already exists")
            return existing_user
        
        # Create demo user
        demo_user = User(
            username="demo",
            password_hash=get_password_hash("demo123")
        )
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
        print(f"Created demo user: {demo_user.username} (password: demo123)")
        return demo_user

def create_demo_case_with_pdfs(user: User):
    """Create a demo case and copy sample PDFs"""
    with Session(engine) as session:
        # Create demo case
        demo_case = Case(
            user_id=user.id,
            name="Sample Case - Legal Documents"
        )
        session.add(demo_case)
        session.commit()
        session.refresh(demo_case)
        print(f"Created demo case: {demo_case.name} (ID: {demo_case.id})")
        
        # Create case directory structure
        case_dir = Path("./data") / str(demo_case.id)
        uploads_dir = case_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy sample PDFs from New_reports
        sample_pdfs_dir = Path("d:/Team_Sisyphus/Team_Sisyphus/New_reports/New_reports")
        if sample_pdfs_dir.exists():
            # Map sample PDFs to expected names
            pdf_mappings = {
                "fir.pdf": "fir.pdf",
                "statement.pdf": "statement.pdf",
                "victim_med_rep.pdf": "victim_med.pdf",
                "accused_med_rep.pdf": "accused_med.pdf"
            }
            
            for source_name, target_name in pdf_mappings.items():
                source_path = sample_pdfs_dir / source_name
                target_path = uploads_dir / target_name
                
                if source_path.exists():
                    shutil.copy2(source_path, target_path)
                    print(f"Copied {source_name} -> {target_name}")
                else:
                    print(f"Warning: {source_name} not found in sample directory")
        else:
            print("Warning: Sample PDFs directory not found")
        
        return demo_case

if __name__ == "__main__":
    print("Seeding CaseFlow database...")
    
    # Create demo user
    demo_user = create_demo_user()
    
    # Create demo case with sample PDFs
    demo_case = create_demo_case_with_pdfs(demo_user)
    
    print("\nSeeding completed!")
    print(f"Demo login: username='demo', password='demo123'")
    print(f"Demo case ID: {demo_case.id}")
    print("\nYou can now:")
    print("1. Start the backend: uvicorn main:app --reload")
    print("2. Start the frontend and login with demo credentials")
    print("3. Use the existing demo case to test the workflow")