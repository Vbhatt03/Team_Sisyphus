from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class JudgmentBase(BaseModel):
    case_title: str
    citation: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None
    tags: Optional[List[str]] = []
    summary: Optional[str] = None
    key_takeaway: str

class Judgment(JudgmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AlertBase(BaseModel):
    title: str
    message: str

class Alert(AlertBase):
    id: int
    case_id: int
    link_to_judgment_id: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CaseBase(BaseModel):
    case_number: str
    fir_details: Optional[dict] = None
    incident_date: Optional[datetime] = None
    fir_date: Optional[datetime] = None

class CaseCreate(CaseBase):
    pass

class Case(CaseBase):
    id: int
    created_at: datetime
    alerts: List[Alert] = []
    model_config = ConfigDict(from_attributes=True)

