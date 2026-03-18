"""
Suggested risk analysis tables (SmartRisk).
Stores generated failure modes, hazards, hazardous situations, harms, controls,
and verification methods per component/source; allows regeneration when component data changes.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class RiskAnalysisSuggestionSet(Base):
    """
    One suggestion set = one rule match on one source (node, interface, or project component).
    Child tables hold the actual suggested text and library references.
    For node/interface: architecture_id set, project_id optional. For component: project_id set, architecture_id null.
    """
    __tablename__ = "risk_analysis_suggestion_sets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    source_type = Column(String(32), nullable=False, index=True)  # "node" | "interface" | "component"
    source_id = Column(String, nullable=False, index=True)  # node_id, interface_id, or component_id
    architecture_id = Column(
        String, ForeignKey("device_architectures.id"), nullable=True, index=True
    )
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)
    rule_id = Column(
        String, ForeignKey("hazard_generation_rules.id"), nullable=False, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    architecture = relationship("DeviceArchitecture", back_populates="suggestion_sets")
    project = relationship("Project", back_populates="risk_analysis_suggestion_sets")
    rule = relationship("HazardGenerationRule", backref="suggestion_sets")
    failure_modes = relationship(
        "SuggestedFailureMode", back_populates="suggestion_set", cascade="all, delete-orphan"
    )
    hazards = relationship(
        "SuggestedHazard", back_populates="suggestion_set", cascade="all, delete-orphan"
    )
    hazardous_situations = relationship(
        "SuggestedHazardousSituation", back_populates="suggestion_set", cascade="all, delete-orphan"
    )
    harms = relationship(
        "SuggestedHarm", back_populates="suggestion_set", cascade="all, delete-orphan"
    )
    controls = relationship(
        "SuggestedControl", back_populates="suggestion_set", cascade="all, delete-orphan"
    )
    verification_methods = relationship(
        "SuggestedVerificationMethod", back_populates="suggestion_set", cascade="all, delete-orphan"
    )


class SuggestedFailureMode(Base):
    __tablename__ = "suggested_failure_modes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="failure_modes"
    )


class SuggestedHazard(Base):
    __tablename__ = "suggested_hazards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    hazard_library_id = Column(String, ForeignKey("hazard_library.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="hazards"
    )


class SuggestedHazardousSituation(Base):
    __tablename__ = "suggested_hazardous_situations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="hazardous_situations"
    )


class SuggestedHarm(Base):
    __tablename__ = "suggested_harms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    harm_library_id = Column(String, ForeignKey("harm_library.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="harms"
    )


class SuggestedControl(Base):
    __tablename__ = "suggested_controls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    risk_control_library_id = Column(
        String, ForeignKey("risk_control_library.id"), nullable=True, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="controls"
    )


class SuggestedVerificationMethod(Base):
    __tablename__ = "suggested_verification_methods"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    suggestion_set_id = Column(
        String, ForeignKey("risk_analysis_suggestion_sets.id"), nullable=False, index=True
    )
    text = Column(Text, nullable=False)
    verification_library_id = Column(
        String, ForeignKey("verification_library.id"), nullable=True, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suggestion_set = relationship(
        "RiskAnalysisSuggestionSet", back_populates="verification_methods"
    )
