"""Project risk items: device/component-scoped risk with library links and risk scoring."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class ProjectRiskItem(Base):
    """
    Risk item scoped to a device and component, with hazard/harm library links,
    risk scores, and residual risk evaluation (ISO 14971 style).
    """
    __tablename__ = "project_risk_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False, index=True)

    failure_mode = Column(Text, nullable=True)
    hazard_library_id = Column(String, ForeignKey("hazard_library.id"), nullable=True, index=True)
    hazard_text = Column(Text, nullable=True)
    hazardous_situation = Column(Text, nullable=True)
    harm_library_id = Column(String, ForeignKey("harm_library.id"), nullable=True, index=True)
    harm_text = Column(Text, nullable=True)

    severity = Column(Integer, nullable=True)
    probability = Column(Integer, nullable=True)
    detectability = Column(Integer, nullable=True)
    risk_score = Column(Integer, nullable=True)
    risk_acceptability = Column(String(64), nullable=True)

    residual_severity = Column(Integer, nullable=True)
    residual_probability = Column(Integer, nullable=True)
    residual_detectability = Column(Integer, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_acceptability = Column(String(64), nullable=True)

    status = Column(String(64), nullable=False, default="open", index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    device = relationship("Device", back_populates="project_risk_items", foreign_keys=[device_id])
    component = relationship("Component", back_populates="project_risk_items", foreign_keys=[component_id])
    hazard_library = relationship("HazardLibrary", foreign_keys=[hazard_library_id])
    harm_library = relationship("HarmLibrary", foreign_keys=[harm_library_id])
    controls = relationship(
        "ProjectRiskControl",
        back_populates="project_risk_item",
        cascade="all, delete-orphan",
    )
