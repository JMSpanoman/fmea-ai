from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class FMEARow(Base):
    __tablename__ = "fmea_rows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=True, index=True)
    
    # FMEA fields
    failure_mode = Column(Text, nullable=True)
    effect = Column(Text, nullable=True)
    cause = Column(Text, nullable=True)
    severity = Column(Integer, nullable=True)
    probability = Column(Integer, nullable=True)
    detection = Column(Integer, nullable=True)
    rpn = Column(Integer, nullable=True)  # Auto-calculated: severity * probability * detection
    mitigation = Column(Text, nullable=True)
    
    # Residual risk fields
    residual_severity = Column(Integer, nullable=True)
    residual_probability = Column(Integer, nullable=True)
    residual_detection = Column(Integer, nullable=True)
    residual_rpn = Column(Integer, nullable=True)  # Auto-calculated: residual_severity * residual_probability * residual_detection
    
    # Financial and AI fields
    financial_impact = Column(Numeric, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Risk Knowledge Base library references (optional)
    hazard_library_id = Column(String, nullable=True, index=True)  # FK to hazard_library.id
    harm_library_id = Column(String, nullable=True, index=True)   # FK to harm_library.id
    risk_control_library_id = Column(String, nullable=True, index=True)  # FK to risk_control_library.id
    verification_library_id = Column(String, nullable=True, index=True)   # FK to verification_library.id
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="fmea_rows")
    component = relationship("Component", back_populates="fmea_rows")
    versions = relationship("FMEAVersion", back_populates="fmea_row", cascade="all, delete-orphan")
    risk_items = relationship("RiskItem", back_populates="fmea_row", cascade="all, delete-orphan")
