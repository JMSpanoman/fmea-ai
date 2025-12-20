from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class ChangeControl(Base):
    __tablename__ = "change_controls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    risk_impact = Column(JSON, nullable=True)
    status = Column(String, nullable=False)  # open, in_review, approved, implemented, verified, closed
    linked_risk_ids = Column(JSON, nullable=True)  # Array of UUIDs
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="change_controls")
