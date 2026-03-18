"""Pydantic schemas for Device Architecture (SmartRisk Phase 1)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ----- DeviceArchitecture -----
class DeviceArchitectureBase(BaseModel):
    name: str
    description: Optional[str] = None


class DeviceArchitectureCreate(DeviceArchitectureBase):
    pass


class DeviceArchitectureUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DeviceArchitectureOut(DeviceArchitectureBase):
    id: str
    project_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----- DeviceArchitectureNode -----
class DeviceArchitectureNodeBase(BaseModel):
    name: str
    description: Optional[str] = None
    node_type: str = Field(..., description="system | subsystem | component")
    component_type: Optional[str] = None
    sort_order: Optional[int] = 0


class DeviceArchitectureNodeCreate(DeviceArchitectureNodeBase):
    parent_id: Optional[str] = None


class DeviceArchitectureNodeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    node_type: Optional[str] = None
    component_type: Optional[str] = None
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None


class DeviceArchitectureNodeOut(DeviceArchitectureNodeBase):
    id: str
    architecture_id: str
    parent_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceArchitectureNodeWithChildren(DeviceArchitectureNodeOut):
    children: List["DeviceArchitectureNodeWithChildren"] = []


DeviceArchitectureNodeWithChildren.model_rebuild()


# ----- DeviceInterface -----
class DeviceInterfaceBase(BaseModel):
    from_node_id: str
    to_node_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    interface_type: Optional[str] = None


class DeviceInterfaceCreate(DeviceInterfaceBase):
    pass


class DeviceInterfaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    interface_type: Optional[str] = None


class DeviceInterfaceOut(DeviceInterfaceBase):
    id: str
    architecture_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----- Tree / full architecture response -----
class DeviceArchitectureDetailOut(DeviceArchitectureOut):
    nodes: List[DeviceArchitectureNodeOut] = []
    interfaces: List[DeviceInterfaceOut] = []


# ----- Hazard generation (Phase 2 / 3) -----
class GenerateHazardsRequest(BaseModel):
    """Optional: create risk items from suggestions (Phase 3 library linking)."""
    create_risk_items: bool = False
    created_by: Optional[str] = None


class GenerateHazardsResponse(BaseModel):
    suggestions: List["SuggestedHazardOut"]
    created_risk_item_ids: Optional[List[str]] = None


# ----- Hazard generation (Phase 2) -----
class SuggestedHazardOut(BaseModel):
    source_type: str  # "node" | "interface"
    source_id: str
    source_name: str
    source_extra: Optional[str] = None
    rule_id: str
    hazard_library_id: str
    hazard_code: Optional[str] = None
    hazard_name: Optional[str] = None
    hazard_description: Optional[str] = None


GenerateHazardsResponse.model_rebuild()


# ----- Hazard log / table (Phase 4 document generation) -----
class HazardLogRowOut(BaseModel):
    """One row for hazard log table export (ISO 14971 traceability)."""
    source_type: str
    source_id: str
    source_name: str
    source_extra: Optional[str] = None
    hazard_code: Optional[str] = None
    hazard_name: Optional[str] = None
    hazard_description: Optional[str] = None
    hazard_library_id: str
    risk_item_id: Optional[str] = None  # if created/linked


class HazardLogTableOut(BaseModel):
    """Hazard log table for document/table generation (Phase 4)."""
    architecture_id: str
    architecture_name: str
    project_id: str
    rows: List[HazardLogRowOut]
