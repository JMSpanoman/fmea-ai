from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from database import Base

class NonConformance(Base):
    __tablename__ = "non_conformances"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    issue_description = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    detection_date = Column(Date, nullable=True)
    severity = Column(String(50), nullable=True)
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    preventive_action = Column(Text, nullable=True)
    action_owner = Column(String(255), nullable=True)
    due_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=True)
    investigation_details = Column(Text, nullable=True)
    regulatory_impact = Column(Text, nullable=True)
    closure_summary = Column(Text, nullable=True)
    analysis_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String(50), default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 