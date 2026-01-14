from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    profile = relationship("ProjectProfile", back_populates="project", uselist=False, cascade="all, delete-orphan")
    components = relationship("Component", back_populates="project", cascade="all, delete-orphan")
    fmea_rows = relationship("FMEARow", back_populates="project", cascade="all, delete-orphan")
    # Phase 2 relationships
    design_inputs = relationship("DesignInput", back_populates="project", cascade="all, delete-orphan")
    design_outputs = relationship("DesignOutput", back_populates="project", cascade="all, delete-orphan")
    vv_tests = relationship("VVTest", back_populates="project", cascade="all, delete-orphan")
    capas = relationship("CAPA", back_populates="project", cascade="all, delete-orphan")
    pms_signals = relationship("PMSSignal", back_populates="project", cascade="all, delete-orphan")
    trace_links = relationship("TraceLink", back_populates="project", cascade="all, delete-orphan")
    # Phase 3 relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    change_controls = relationship("ChangeControl", back_populates="project", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="project", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="project", cascade="all, delete-orphan")
    ncrs = relationship("NCR", back_populates="project", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="project", cascade="all, delete-orphan")
    equipment = relationship("Equipment", back_populates="project", cascade="all, delete-orphan")
    quality_events = relationship("QualityEvent", back_populates="project", cascade="all, delete-orphan")
    risk_items = relationship("RiskItem", back_populates="project", cascade="all, delete-orphan")
    risk_management_plans = relationship("RiskManagementPlan", back_populates="project", cascade="all, delete-orphan")
