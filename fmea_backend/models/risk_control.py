from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class RiskControl(Base):
    """Risk control measures (ISO 14971 compliant)"""
    __tablename__ = "risk_controls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # SmartQS Risk schema fields
    control_key = Column(String(50), nullable=True, index=True)  # Unique within risk item identifier (e.g., RC-003)
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Creator user ID
    
    # Control identification
    control_name = Column(String, nullable=False)
    control_description = Column(Text, nullable=True)
    control_type = Column(String, nullable=False)  # "inherent_safety", "protective", "information"
    
    # Control details
    implementation_details = Column(Text, nullable=True)  # How the control is implemented
    verification_method = Column(Text, nullable=True)  # How control effectiveness is verified
    trace_to_design_input = Column(String, nullable=True)  # Link to design input ID
    trace_to_design_output = Column(String, nullable=True)  # Link to design output ID
    trace_to_verification_test = Column(String, nullable=True)  # Link to V&V test ID
    
    # Status
    status = Column(String, nullable=False, default="proposed")  # "proposed", "active", "retired"
    
    # Ownership
    owner = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)
    
    # Dates
    proposed_date = Column(DateTime(timezone=True), nullable=True)
    implemented_date = Column(DateTime(timezone=True), nullable=True)
    verified_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    effectiveness_notes = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    risk_item = relationship("RiskItem", back_populates="controls", foreign_keys=[risk_item_id])
    project = relationship("Project", foreign_keys=[project_id])
    creator = relationship("User", foreign_keys=[created_by])

