from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
from typing import Optional, List
import json

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Case(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta: Optional[str] = Field(default=None)  # JSON string for additional metadata
    
    def get_meta(self) -> dict:
        return json.loads(self.meta) if self.meta else {}
    
    def set_meta(self, data: dict):
        self.meta = json.dumps(data)

class ChecklistItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")
    section: str
    text: str
    checked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CaseDiaryPage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    case_id: int = Field(foreign_key="case.id")
    page_number: int
    content: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Database setup
DATABASE_URL = "sqlite:///./caseflow.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session