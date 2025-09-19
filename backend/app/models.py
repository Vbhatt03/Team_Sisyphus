from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .database import Base
from pgvector.sqlalchemy import Vector as PGVector
from sqlalchemy.sql import func
import datetime

class Judgment(Base):
    __tablename__ = "judgments"
    id = Column(Integer, primary_key=True, index=True)
    case_title = Column(String, nullable=False)
    citation = Column(String)
    court = Column(String)
    year = Column(Integer)
    tags = Column(ARRAY(String))
    summary = Column(Text)
    key_takeaway = Column(Text, nullable=False)
    embedding = Column(PGVector(384))

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True)
    fir_details = Column(JSON)
    incident_date = Column(TIMESTAMP(timezone=True))
    fir_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link_to_judgment_id = Column(Integer, ForeignKey("judgments.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    case = relationship("Case", back_populates="alerts")
    judgment = relationship("Judgment")

