from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class AuditLogEvent(Base):
    """Audit log for system events like handoffs, approvals, etc."""
    __tablename__ = "audit_log_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Event classification
    event_type = Column(String, nullable=False, index=True)  # "handoff.design.created", "handoff.capa.created", etc.
    
    # Event details
    details_json = Column(JSON, nullable=True)  # Flexible JSON for event-specific data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    project = relationship("Project")
    user = relationship("User", foreign_keys=[user_id])

