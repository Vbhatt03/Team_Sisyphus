import json
from sqlalchemy.orm import Session
from . import models, schemas
from sentence_transformers import SentenceTransformer
from datetime import datetime

# Load the model once when the service starts. This is a lightweight, effective model.
model = SentenceTransformer('all-MiniLM-L6-v2')

def find_similar_judgments(db: Session, query: str, top_k: int = 5):
    """Finds judgments semantically similar to the query."""
    query_embedding = model.encode(query)
    results = db.query(models.Judgment).order_by(models.Judgment.embedding.l2_distance(query_embedding)).limit(top_k).all()
    return results

def run_case_diagnostics(db: Session, case: models.Case):
    """Runs a set of rules against a case to generate alerts."""
    try:
        with open("data/rules.json", "r") as f:
            rules = json.load(f)
    except FileNotFoundError:
        print("Warning: rules.json not found. No diagnostics will be run.")
        return

    for rule in rules:
        try:
            # WARNING: Using eval is a security risk in a real production environment.
            # This is simplified for the MVP. A real implementation should use a
            # safer rule evaluation engine (e.g., custom parsing).
            if eval(rule["condition"], {"case": case, "datetime": datetime}):
                precedent = db.query(models.Judgment).filter(models.Judgment.tags.contains([rule["relevant_precedent_tag"]])).first()
                
                delay_days = (case.fir_date - case.incident_date).days if case.fir_date and case.incident_date else 0
                message = rule["alert_message_template"].format(delay_days=delay_days)

                alert = models.Alert(
                    case_id=case.id,
                    title=rule["alert_title"],
                    message=message,
                    link_to_judgment_id=precedent.id if precedent else None
                )
                db.add(alert)
                db.commit()
        except Exception as e:
            print(f"Error evaluating rule '{rule['rule_id']}': {e}")

def create_case_and_run_diagnostics(db: Session, case: schemas.CaseCreate) -> models.Case:
    """Creates a case and then triggers the diagnostics."""
    db_case = models.Case(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    
    run_case_diagnostics(db, db_case)
    
    db.refresh(db_case)
    return db_case

