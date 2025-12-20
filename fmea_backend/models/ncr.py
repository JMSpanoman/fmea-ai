from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class NCR(Base):
    __tablename__ = "ncrs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    containment_action = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    linked_risk_ids = Column(JSON, nullable=True)  # Array of UUIDs
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="ncrs")

