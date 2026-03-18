"""
Device Architecture schema for SmartRisk (ISO 14971).
Structured representation of the medical device for architecture-driven hazard analysis.
Phase 1 of the hazard generation engine.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class DeviceArchitecture(Base):
    """
    Top-level device architecture for a project.
    One project can have multiple architectures (e.g. variants, versions).
    """
    __tablename__ = "device_architectures"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="device_architectures")
    nodes = relationship(
        "DeviceArchitectureNode",
        back_populates="architecture",
        cascade="all, delete-orphan",
        foreign_keys="DeviceArchitectureNode.architecture_id",
    )
    interfaces = relationship(
        "DeviceInterface",
        back_populates="architecture",
        cascade="all, delete-orphan",
    )
    suggestion_sets = relationship(
        "RiskAnalysisSuggestionSet",
        back_populates="architecture",
        cascade="all, delete-orphan",
        foreign_keys="RiskAnalysisSuggestionSet.architecture_id",
    )


class DeviceArchitectureNode(Base):
    """
    Hierarchy node: system, subsystem, or component.
    component_type supports rule matching (e.g. electrical, mechanical, software).
    """
    __tablename__ = "device_architecture_nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    architecture_id = Column(
        String, ForeignKey("device_architectures.id"), nullable=False, index=True
    )
    parent_id = Column(
        String, ForeignKey("device_architecture_nodes.id"), nullable=True, index=True
    )
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    node_type = Column(String(64), nullable=False, index=True)  # system | subsystem | component
    component_type = Column(String(128), nullable=True, index=True)  # e.g. electrical, mechanical, software
    sort_order = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    architecture = relationship(
        "DeviceArchitecture",
        back_populates="nodes",
        foreign_keys=[architecture_id],
    )
    parent = relationship(
        "DeviceArchitectureNode",
        remote_side=[id],
        back_populates="children",
        uselist=False,
    )
    children = relationship("DeviceArchitectureNode", back_populates="parent")
    interfaces_from = relationship(
        "DeviceInterface",
        foreign_keys="DeviceInterface.from_node_id",
        back_populates="from_node",
    )
    interfaces_to = relationship(
        "DeviceInterface",
        foreign_keys="DeviceInterface.to_node_id",
        back_populates="to_node",
    )


class DeviceInterface(Base):
    """
    Interface between two nodes (e.g. power, data, mechanical).
    interface_type supports rule-based hazard generation.
    """
    __tablename__ = "device_interfaces"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    architecture_id = Column(
        String, ForeignKey("device_architectures.id"), nullable=False, index=True
    )
    from_node_id = Column(
        String, ForeignKey("device_architecture_nodes.id"), nullable=False, index=True
    )
    to_node_id = Column(
        String, ForeignKey("device_architecture_nodes.id"), nullable=False, index=True
    )
    name = Column(String(256), nullable=True)
    description = Column(Text, nullable=True)
    interface_type = Column(String(128), nullable=True, index=True)  # e.g. electrical, data, mechanical
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    architecture = relationship("DeviceArchitecture", back_populates="interfaces")
    from_node = relationship(
        "DeviceArchitectureNode",
        foreign_keys=[from_node_id],
        back_populates="interfaces_from",
    )
    to_node = relationship(
        "DeviceArchitectureNode",
        foreign_keys=[to_node_id],
        back_populates="interfaces_to",
    )
