import json
import os
import sys
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
import multiprocessing # <-- ADD THIS LINE

# Add backend directory to path to import app models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.models import Judgment
from app.database import Base

# --- CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nyaya_user:nyaya_password@localhost:5432/nyaya_db")
JUDGMENTS_FILE = "data/judgements/judgements.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print(f"Loading sentence transformer model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    # Wait for DB to be ready
    retries = 5
    while retries > 0:
        try:
            connection = engine.connect()
            connection.close()
            print("Database connection successful.")
            break
        except Exception as e:
            print(f"Database not ready, retrying... ({retries} left)")
            retries -= 1
            time.sleep(5)
    if retries == 0:
        print("Could not connect to the database. Aborting.")
        sys.exit(1)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print(f"Reading judgments from {JUDGMENTS_FILE}...")
    with open(JUDGMENTS_FILE, 'r') as f:
        judgments_data = json.load(f)

    print(f"Found {len(judgments_data)} judgments. Processing and embedding...")

    for item in judgments_data:
        exists = db.query(Judgment).filter(Judgment.case_title == item['case_title']).first()
        if exists:
            print(f"Skipping existing judgment: {item['case_title']}")
            continue

        text_to_embed = f"Title: {item['case_title']}. Takeaway: {item['key_takeaway']}"
        embedding = model.encode(text_to_embed).tolist()

        new_judgment = Judgment(
            case_title=item['case_title'],
            citation=item.get('citation'),
            court=item.get('court'),
            year=item.get('year'),
            tags=item.get('tags', []),
            summary=item.get('summary'),
            key_takeaway=item['key_takeaway'],
            embedding=embedding
        )
        db.add(new_judgment)
        print(f"Added and embedded: {item['case_title']}")

    print("Committing changes to the database...")
    db.commit()
    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    # This forces Python to use the 'spawn' start method, which is safer on macOS
    # and avoids the deadlock issue with the sentence-transformers library.
    multiprocessing.set_start_method("spawn", force=True) # <-- ADD THIS LINE
    main()