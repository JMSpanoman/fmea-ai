from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class RiskItemVersion(Base):
    """Immutable snapshot of a risk item at a point in time (ISO 14971 compliant)"""
    __tablename__ = "risk_item_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, default=1)
    
    # ISO 14971: Hazard analysis chain
    hazard = Column(Text, nullable=True)  # Potential source of harm
    hazardous_situation = Column(Text, nullable=True)  # Circumstance in which people/property are exposed to hazards
    harm = Column(Text, nullable=True)  # Physical injury or damage to health/property
    failure_mode = Column(Text, nullable=True)  # FMEA-style failure mode (optional)
    sequence_of_events = Column(Text, nullable=True)  # Optional: how hazard leads to harm
    
    # Risk estimation (ISO 14971 compliant)
    severity = Column(Integer, nullable=True)  # Severity of harm (1-10 scale)
    probability_of_harm = Column(Integer, nullable=True)  # Probability of occurrence (1-10 scale, canonical)
    occurrence = Column(Integer, nullable=True)  # Alias for probability_of_harm (FMEA style)
    detection = Column(Integer, nullable=True)  # Detection capability (FMEA style, 1-10)
    
    # Legacy fields (backward compatibility)
    probability = Column(Integer, nullable=True)  # Legacy alias
    impact = Column(Integer, nullable=True)  # Legacy field
    
    # Calculated risk metrics
    risk_score = Column(Integer, nullable=True)  # severity * probability_of_harm * (detection or 1)
    risk_level = Column(String, nullable=True)  # "Low", "Medium", "High", "Critical"
    
    # Risk control measures (ISO 14971)
    inherent_safety = Column(Text, nullable=True)  # Inherently safe design measures
    protective_measures = Column(Text, nullable=True)  # Protective measures in medical device/software
    information_for_safety = Column(Text, nullable=True)  # Information for safety (labeling, instructions)
    control_measures_summary = Column(Text, nullable=True)  # Summary of all control measures
    
    # Residual risk evaluation (ISO 14971)
    residual_severity = Column(Integer, nullable=True)
    residual_probability_of_harm = Column(Integer, nullable=True)
    residual_occurrence = Column(Integer, nullable=True)  # Alias
    residual_detection = Column(Integer, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)  # After controls applied
    residual_risk_level = Column(String, nullable=True)
    
    # Benefit-risk analysis (ISO 14971)
    benefit_risk_summary = Column(Text, nullable=True)  # Benefit-risk evaluation summary
    overall_residual_risk_conclusion = Column(Text, nullable=True)  # Final conclusion on residual risk acceptability
    
    # Risk acceptability (ISO 14971)
    risk_acceptability = Column(String, nullable=True)  # "acceptable", "unacceptable", "needs_benefit_risk"
    risk_rationale = Column(Text, nullable=True)  # Rationale for risk acceptability decision
    
    # Metadata
    change_summary = Column(Text, nullable=True)  # Summary of changes from previous version
    changed_by = Column(String, nullable=True)  # User ID who made the change
    ai_metadata = Column(JSON, nullable=True)  # AI suggestions metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    risk_item = relationship("RiskItem", back_populates="versions", foreign_keys=[risk_item_id])

