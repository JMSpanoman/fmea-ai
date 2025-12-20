from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class DesignOutput(Base):
    __tablename__ = "design_outputs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    source = Column(String, nullable=False)  # "ai" or "user"
    text = Column(Text, nullable=False)
    linked_input_id = Column(String, ForeignKey("design_inputs.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="design_outputs")
    design_input = relationship("DesignInput", back_populates="design_outputs")
    vv_tests = relationship("VVTest", back_populates="design_output", cascade="all, delete-orphan")

