from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Audit(Base):
    __tablename__ = "audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # internal, supplier, external, regulatory
    scope = Column(Text, nullable=True)
    findings = Column(JSON, nullable=True)
    status = Column(String, nullable=False)
    ai_metadata = Column(JSON, nullable=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="audits")

