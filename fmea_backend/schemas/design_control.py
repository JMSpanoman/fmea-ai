from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime

DesignArtifactStatus = Literal["draft", "approved", "implemented", "obsolete"]


class DesignInputBase(BaseModel):
    # Required minimal fields for Design Inputs Documentation
    title: str
    requirement_text: str
    status: DesignArtifactStatus = "draft"

    # Backward compatibility fields (existing API/UI)
    text: Optional[str] = None
    requirement: Optional[str] = None
    source: str = "user"  # "ai" or "user"
    linked_risk_ids: Optional[List[str]] = None  # Array of UUIDs

class DesignInputCreate(DesignInputBase):
    project_id: str  # UUID
    di_key: Optional[str] = None  # Optional stable key like DI-014 (auto-generated if absent)

class DesignInputUpdate(BaseModel):
    title: Optional[str] = None
    requirement_text: Optional[str] = None
    status: Optional[DesignArtifactStatus] = None
    text: Optional[str] = None
    requirement: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None

class DesignInputOut(DesignInputBase):
    id: str  # UUID
    project_id: str  # UUID
    di_key: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DesignOutputBase(BaseModel):
    text: str
    source: str  # "ai" or "user"
    linked_input_id: Optional[str] = None  # UUID

class DesignOutputCreate(DesignOutputBase):
    project_id: str  # UUID

class DesignOutputUpdate(BaseModel):
    text: Optional[str] = None
    linked_input_id: Optional[str] = None

class DesignOutputOut(DesignOutputBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Generation Request/Response
class DesignControlsGenerateRequest(BaseModel):
    project_id: str  # UUID
    component_id: Optional[str] = None  # UUID
    risk_ids: Optional[List[str]] = None  # Array of FMEA row UUIDs

class DesignControlsGenerateResponse(BaseModel):
    design_inputs: List[DesignInputOut]
    design_outputs: List[DesignOutputOut]
    trace_links: List[dict]  # Array of trace link objects

