from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class RiskItem(Base):
    __tablename__ = "risk_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id"), nullable=True, index=True)
    current_version_id = Column(String, nullable=True, index=True)  # FK handled in migration/application
    
    # SmartQS Risk schema fields
    risk_key = Column(String(50), nullable=True, index=True)  # Unique per project identifier (e.g., R-023)
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Creator user ID
    
    # Risk identification
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "Safety", "Quality", "Financial", "Compliance"
    risk_type = Column(String, nullable=True)  # e.g., "Hazard", "Failure", "Non-compliance"
    
    # Risk assessment (backward compatible)
    severity = Column(Integer, nullable=True)  # 1-10 scale
    probability = Column(Integer, nullable=True)  # 1-10 scale (legacy)
    impact = Column(Integer, nullable=True)  # 1-10 scale (legacy)
    risk_score = Column(Integer, nullable=True)  # Auto-calculated: severity * probability * impact
    risk_level = Column(String, nullable=True)  # "Low", "Medium", "High", "Critical"
    
    # Risk control
    mitigation_strategy = Column(Text, nullable=True)
    control_measures = Column(Text, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)  # Legacy
    residual_risk_level = Column(String, nullable=True)  # Legacy
    
    # Ownership and status
    owner = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")  # "open", "mitigated", "closed", "accepted"
    priority = Column(String, nullable=True)  # "Low", "Medium", "High", "Urgent"
    
    # Additional metadata
    source = Column(String, nullable=True)  # e.g., "FMEA", "Audit", "Complaint", "PMS"
    detected_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    closed_date = Column(DateTime(timezone=True), nullable=True)
    
    # AI and metadata
    ai_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="risk_items")
    fmea_row = relationship("FMEARow", back_populates="risk_items")
    creator = relationship("User", foreign_keys=[created_by])
    current_version = relationship("RiskItemVersion", foreign_keys=[current_version_id], post_update=True, remote_side="RiskItemVersion.id")
    versions = relationship("RiskItemVersion", back_populates="risk_item", foreign_keys="RiskItemVersion.risk_item_id", cascade="all, delete-orphan", order_by="RiskItemVersion.version_number")
    controls = relationship("RiskControl", back_populates="risk_item", cascade="all, delete-orphan")

