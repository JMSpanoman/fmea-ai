"""
Hazard Analysis Item model — ISO 14971-style hazard analysis row.
Full schema for SmartRisk Hazard Analysis report with traceability to risk items/FMEA.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class HazardAnalysisItem(Base):
    """
    Single hazard analysis row with full ISO 14971 fields.
    Can be linked to risk_item_id/risk_item_version_id for traceability.
    """
    __tablename__ = "hazard_analysis_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=True, index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=True, index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=True, index=True)
    risk_item_version_id = Column(String, ForeignKey("risk_item_versions.id"), nullable=True, index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id"), nullable=True, index=True)

    # --- Core fields ---
    risk_key = Column(String(50), nullable=True, index=True)
    version_no = Column(Integer, nullable=False, default=1)
    hazard_category = Column(String(255), nullable=True, index=True)
    hazard = Column(Text, nullable=True)
    foreseeable_sequence_of_events = Column(Text, nullable=True)
    sequence_of_events = Column(Text, nullable=True)  # alias/backward-compatible copy
    hazardous_situation = Column(Text, nullable=True)
    harm = Column(Text, nullable=True)
    affected_user = Column(String(255), nullable=True)
    failure_mode = Column(Text, nullable=True)
    cause_of_failure = Column(Text, nullable=True)
    clinical_effect = Column(Text, nullable=True)
    operating_mode = Column(String(255), nullable=True)
    use_environment = Column(Text, nullable=True)

    # --- Initial risk estimation ---
    initial_severity = Column(Integer, nullable=True)
    initial_probability = Column(Integer, nullable=True)
    initial_occurrence = Column(Integer, nullable=True)  # alias for probability
    initial_risk_level = Column(String(50), nullable=True)

    # --- Risk controls ---
    risk_control_measures = Column(JSON, nullable=True)  # list of strings
    risk_control_type = Column(JSON, nullable=True)  # list: e.g. ["inherent_safety", "protective"]
    control_implementation_notes = Column(Text, nullable=True)
    risk_controls = Column(JSON, nullable=True)  # [{control_type, control_description, implementation_status, verification_method, verification_status}]

    # --- Residual risk ---
    residual_severity = Column(Integer, nullable=True)
    residual_probability = Column(Integer, nullable=True)
    residual_occurrence = Column(Integer, nullable=True)  # alias for probability
    residual_risk_level = Column(String(50), nullable=True)
    residual_risk_acceptability = Column(String(100), nullable=True)
    risk_acceptability_decision = Column(String(100), nullable=True)
    risk_acceptability_justification = Column(Text, nullable=True)

    # --- Traceability ---
    related_design_input = Column(JSON, nullable=True)  # list of ids or refs
    related_design_output = Column(JSON, nullable=True)
    verification_reference = Column(JSON, nullable=True)  # list of refs
    validation_reference = Column(JSON, nullable=True)
    requirement_ids = Column(JSON, nullable=True)  # list of strings
    capa_reference = Column(JSON, nullable=True)  # list of CAPA ids/refs

    # --- Review / workflow ---
    approval_status = Column(String(50), nullable=True, default="draft", index=True)  # draft, in_review, approved, rejected
    approved_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approver_role = Column(String(255), nullable=True)
    approval_meaning = Column(Text, nullable=True)
    version_lock = Column(Boolean, nullable=False, default=False)
    reviewer_comments = Column(Text, nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    review_frequency = Column(String(255), nullable=True)  # e.g. monthly, quarterly
    last_reviewed_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    post_market_trigger = Column(Boolean, nullable=False, default=False)

    benefit_risk_analysis_required = Column(Boolean, nullable=False, default=False)
    benefit_risk_justification = Column(Text, nullable=True)

    # --- Metadata ---
    ai_generated = Column(Boolean, nullable=True, default=False)
    ai_confidence = Column(String(50), nullable=True)  # e.g. "high", "medium", "low"
    source_context = Column(Text, nullable=True)
    assumptions = Column(JSON, nullable=True)  # list of strings

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    project = relationship("Project", backref="hazard_analysis_items")
    component = relationship("Component", backref="hazard_analysis_items", foreign_keys=[component_id])
    device = relationship("Device", backref="hazard_analysis_items", foreign_keys=[device_id])
    risk_item = relationship("RiskItem", backref="hazard_analysis_items", foreign_keys=[risk_item_id])
    risk_item_version = relationship("RiskItemVersion", backref="hazard_analysis_items", foreign_keys=[risk_item_version_id])
    fmea_row = relationship("FMEARow", backref="hazard_analysis_items", foreign_keys=[fmea_row_id])
    approver = relationship("User", foreign_keys=[approved_by])
    creator = relationship("User", foreign_keys=[created_by])
    last_reviewer = relationship("User", foreign_keys=[last_reviewed_by])
