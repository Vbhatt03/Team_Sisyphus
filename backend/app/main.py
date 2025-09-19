from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, services, database
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# This line is crucial for SQLAlchemy to create the tables based on your models
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="NYAYA AI API")

# CORS Middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Allows the React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NYAYA AI Judicial Intelligence Engine"}

@app.get("/api/judgments/search", response_model=List[schemas.Judgment])
def search_judgments(q: str, db: Session = Depends(database.get_db)):
    """
    Search for judgments based on a query using semantic vector search.
    """
    if not q:
        return []
    return services.find_similar_judgments(db, q)

@app.post("/api/cases", response_model=schemas.Case)
def create_case(case: schemas.CaseCreate, db: Session = Depends(database.get_db)):
    """
    Create a new case and run initial diagnostics to generate proactive alerts.
    """
    new_case = services.create_case_and_run_diagnostics(db, case)
    return new_case

@app.get("/api/cases/{case_id}/alerts", response_model=List[schemas.Alert])
def get_case_alerts(case_id: int, db: Session = Depends(database.get_db)):
    """
    Get all proactive alerts for a specific case.
    """
    alerts = db.query(models.Alert).filter(models.Alert.case_id == case_id).all()
    return alerts

