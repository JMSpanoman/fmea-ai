from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChangeControlBase(BaseModel):
    title: str
    description: Optional[str] = None
    reason: Optional[str] = None
    status: str  # open, in_review, approved, implemented, verified, closed
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class ChangeControlCreate(ChangeControlBase):
    project_id: str  # UUID

class ChangeControlUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    risk_impact: Optional[Dict[str, Any]] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class ChangeControlOut(ChangeControlBase):
    id: str  # UUID
    project_id: str  # UUID
    risk_impact: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# AI Change Control Impact Analysis
class ChangeControlImpactRequest(BaseModel):
    change_control_id: str  # UUID

class ChangeControlImpactResponse(BaseModel):
    affected_risks: List[str]  # Array of risk IDs
    affected_design_inputs: List[str]  # Array of design input IDs
    affected_design_outputs: List[str]  # Array of design output IDs
    affected_vv_tests: List[str]  # Array of V&V test IDs
    affected_capas: List[str]  # Array of CAPA IDs
    affected_pms_signals: List[str]  # Array of PMS signal IDs
    ai_metadata: Optional[Dict[str, Any]] = None
