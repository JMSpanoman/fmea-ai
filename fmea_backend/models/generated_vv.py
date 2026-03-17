"""Stores AI-generated V&V test logic from FMEA/risk rows for traceability and later protocol generation."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class GeneratedVVRecord(Base):
    __tablename__ = "generated_vv_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id"), nullable=True, index=True)
    risk_item_id = Column(String, ForeignKey("risk_items.id"), nullable=True, index=True)

    verification_test_name = Column(String(512), nullable=False)
    verification_objective = Column(Text, nullable=True)
    verification_method = Column(Text, nullable=True)
    validation_test_name = Column(String(512), nullable=True)
    validation_objective = Column(Text, nullable=True)
    validation_scenario = Column(Text, nullable=True)  # validation_method_or_scenario
    acceptance_criteria = Column(JSON, nullable=True)  # list of strings
    calculations = Column(JSON, nullable=True)  # list of {name, formula, description, inputs, unit_or_threshold}
    worst_case_conditions = Column(JSON, nullable=True)  # list of strings
    sample_size_rationale = Column(Text, nullable=True)
    traceability = Column(JSON, nullable=True)  # full traceability block

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")
    fmea_row = relationship("FMEARow", foreign_keys=[fmea_row_id])
    risk_item = relationship("RiskItem", foreign_keys=[risk_item_id])
