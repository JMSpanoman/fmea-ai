from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DesignInputBase(BaseModel):
    text: str
    source: str  # "ai" or "user"
    linked_risk_ids: Optional[List[str]] = None  # Array of UUIDs

class DesignInputCreate(DesignInputBase):
    project_id: str  # UUID

class DesignInputUpdate(BaseModel):
    text: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None

class DesignInputOut(DesignInputBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

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

