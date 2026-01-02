from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class VVTest(Base):
    __tablename__ = "vv_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    design_output_id = Column(String, ForeignKey("design_outputs.id"), nullable=False, index=True)
    
    # SmartQS Design schema fields
    vv_key = Column(String(50), nullable=True, index=True)  # Optional stable key like V-007
    name = Column(String(255), nullable=True)  # Test name
    test_method = Column(Text, nullable=False)  # Method
    acceptance_criteria = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="draft")  # Status
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Creator user ID
    rationale = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="vv_tests")
    creator = relationship("User", foreign_keys=[created_by])
    design_output = relationship("DesignOutput", back_populates="vv_tests")

