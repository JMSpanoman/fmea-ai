from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class DesignOutput(Base):
    __tablename__ = "design_outputs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # SmartQS Design schema fields
    do_key = Column(String(50), nullable=True, index=True)  # Optional stable key like DO-009
    title = Column(String(255), nullable=True)  # Title or name
    source = Column(String, nullable=False)  # "ai" or "user"
    text = Column(Text, nullable=False)  # Description (kept for backward compatibility)
    description = Column(Text, nullable=True)  # Description (alias for text)
    document_ref = Column(String(255), nullable=True)  # Optional pointer to controlled doc
    status = Column(String(50), nullable=False, default="draft")  # Status
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Creator user ID
    linked_input_id = Column(String, ForeignKey("design_inputs.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="design_outputs")
    creator = relationship("User", foreign_keys=[created_by])
    design_input = relationship("DesignInput", back_populates="design_outputs")
    vv_tests = relationship("VVTest", back_populates="design_output", cascade="all, delete-orphan")

