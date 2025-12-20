from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    calibration_due = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="equipment")
    calibration_records = relationship("CalibrationRecord", back_populates="equipment", cascade="all, delete-orphan")

class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False, index=True)
    performed_at = Column(DateTime(timezone=True), nullable=False)
    result = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    equipment = relationship("Equipment", back_populates="calibration_records")

