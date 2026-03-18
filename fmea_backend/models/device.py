"""Device entity for project risk items (references from project_risk_items.device_id)."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class Device(Base):
    """
    Device definition or instance, scoped to a project.
    Referenced by project_risk_items to associate risk with a specific device.
    """
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(256), nullable=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="devices", foreign_keys=[project_id])
    project_risk_items = relationship(
        "ProjectRiskItem",
        back_populates="device",
        foreign_keys="ProjectRiskItem.device_id",
        cascade="all, delete-orphan",
    )
    generated_documents = relationship(
        "GeneratedDocument",
        back_populates="device",
        foreign_keys="GeneratedDocument.device_id",
        cascade="all, delete-orphan",
    )
