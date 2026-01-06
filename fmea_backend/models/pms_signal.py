from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Date, Integer, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class PMSSignal(Base):
    __tablename__ = "pms_signals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Signal identification
    signal_key = Column(String(50), nullable=False, index=True)  # e.g., PMS-012
    signal_type = Column(String(50), nullable=False, index=True)  # complaint | field_data | trend | service | literature
    component_names_json = Column(JSON, nullable=False)  # List of component names
    
    # Signal details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_ref = Column(String(255), nullable=True)  # complaint id, ticket id, lot #, etc.
    date_detected = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Observed metrics
    severity_observed = Column(Integer, nullable=True)
    frequency_observed = Column(Integer, nullable=True)
    rate_observed = Column(Numeric, nullable=True)
    
    # Status fields
    trend_status = Column(String(50), nullable=False, default='under_review', index=True)  # none | under_review | confirmed | false_alarm
    trigger_status = Column(String(50), nullable=False, default='not_triggered', index=True)  # not_triggered | risk_review_required | capa_required | change_required
    recommended_action = Column(Text, nullable=True)
    owner = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default='open', index=True)  # open | investigating | closed
    
    # Metadata
    created_by = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="pms_signals")
    creator = relationship("User", foreign_keys=[created_by])
