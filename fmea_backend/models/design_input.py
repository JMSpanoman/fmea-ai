from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class DesignInput(Base):
    __tablename__ = "design_inputs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    source = Column(String, nullable=False)  # "ai" or "user"
    text = Column(Text, nullable=False)
    linked_risk_ids = Column(JSON, nullable=True)  # Array of UUIDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="design_inputs")
    design_outputs = relationship("DesignOutput", back_populates="design_input", cascade="all, delete-orphan")

