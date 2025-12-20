from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class AIEvent(Base):
    """AI usage logging for audit trail and governance"""
    __tablename__ = "ai_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Context
    context_type = Column(String, nullable=False)  # "risk_item", "fmea", "capa", etc.
    context_id = Column(String, nullable=True, index=True)  # ID of the artifact AI was used on
    
    # AI details
    prompt_name = Column(String, nullable=False)  # "risk_suggest", "fmea_generate", etc.
    input_summary = Column(Text, nullable=True)  # Summary of inputs (for privacy)
    output_json = Column(JSON, nullable=True)  # Full AI output
    
    # Disposition tracking
    disposition = Column(String, nullable=True)  # "accepted", "edited", "rejected", "pending"
    disposition_notes = Column(Text, nullable=True)
    disposition_user_id = Column(String, nullable=True)  # Who made the disposition
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    disposed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project")
    user = relationship("User", foreign_keys=[user_id])

