from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class PMSSignal(Base):
    __tablename__ = "pms_signals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    signal_type = Column(String, nullable=False)  # complaint, service_data, trending, audit, field_failure
    description = Column(Text, nullable=False)
    linked_risk_ids = Column(JSON, nullable=True)  # Array of UUIDs
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="pms_signals")

