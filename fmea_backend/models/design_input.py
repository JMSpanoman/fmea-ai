from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class DesignInput(Base):
    __tablename__ = "design_inputs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # SmartQS Design schema fields
    di_key = Column(String(50), nullable=True, index=True)  # Optional stable key like DI-014
    title = Column(String(255), nullable=True)  # Title or name
    source = Column(String, nullable=False)  # "ai" or "user" (or user need / standard / risk control)
    text = Column(Text, nullable=False)  # Requirement text (kept for backward compatibility)
    requirement = Column(Text, nullable=True)  # Requirement text (alias for text)
    status = Column(String(50), nullable=False, default="draft")  # draft/approved/implemented/obsolete
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Creator user ID
    linked_risk_ids = Column(JSON, nullable=True)  # Array of UUIDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="design_inputs")
    creator = relationship("User", foreign_keys=[created_by])
    design_outputs = relationship("DesignOutput", back_populates="design_input", cascade="all, delete-orphan")

