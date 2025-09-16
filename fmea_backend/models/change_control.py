from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class ChangeControl(Base):
    __tablename__ = "change_controls"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    change_description = Column(Text, nullable=False)
    initiator = Column(String(255), nullable=False)
    date_initiated = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    impact_assessment = Column(Text, nullable=True)
    actions_required = Column(Text, nullable=True)
    action_owner = Column(String(255), nullable=True)
    due_date = Column(String(50), nullable=True)
    closure_summary = Column(Text, nullable=True)
    analysis_timestamp = Column(String(50), nullable=True)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 