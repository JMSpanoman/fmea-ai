"""
Hazard Generation Rules for SmartRisk (Phase 2).
Admin-editable rules mapping component/interface types to hazard library entries.
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class HazardGenerationRule(Base):
    """
    Rule: when a node or interface matches (component_type or interface_type),
    suggest a hazard from the hazard library.
    Global rules (not project-specific) for reuse across projects.
    """
    __tablename__ = "hazard_generation_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(256), nullable=True)
    trigger_type = Column(String(32), nullable=False, index=True)  # "component" | "interface"
    component_type = Column(String(128), nullable=True, index=True)  # e.g. electrical, mechanical
    interface_type = Column(String(128), nullable=True, index=True)  # e.g. electrical, data
    node_type = Column(String(64), nullable=True, index=True)  # optional filter: system, subsystem, component
    hazard_library_id = Column(String, ForeignKey("hazard_library.id"), nullable=False, index=True)
    harm_library_id = Column(String, ForeignKey("harm_library.id"), nullable=True, index=True)
    risk_control_library_id = Column(String, ForeignKey("risk_control_library.id"), nullable=True, index=True)
    verification_library_id = Column(String, ForeignKey("verification_library.id"), nullable=True, index=True)
    failure_mode_template = Column(Text, nullable=True)  # e.g. "{{component_name}} fails to ..."
    hazardous_situation_template = Column(Text, nullable=True)
    priority = Column(Integer, nullable=True, default=0)  # higher = applied first
    is_active = Column(Boolean, default=True, nullable=False)
    condition_json = Column(Text, nullable=True)  # future: JSON for extra conditions (AI-ready)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    hazard_library = relationship("HazardLibrary", backref="generation_rules")
    harm_library = relationship("HarmLibrary", backref="generation_rules")
    risk_control_library = relationship("RiskControlLibrary", backref="generation_rules")
    verification_library = relationship("VerificationLibrary", backref="generation_rules")
