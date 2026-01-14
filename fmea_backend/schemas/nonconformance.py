from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class NonConformanceBase(BaseModel):
    issue_description: str
    source: Optional[str] = None
    detection_date: Optional[date] = None
    severity: Optional[str] = None
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    preventive_action: Optional[str] = None
    action_owner: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    investigation_details: Optional[str] = None
    regulatory_impact: Optional[str] = None
    closure_summary: Optional[str] = None
    analysis_timestamp: Optional[datetime] = None
    version: Optional[str] = "1.0"

class NonConformanceCreate(NonConformanceBase):
    pass

class NonConformanceUpdate(NonConformanceBase):
    pass

class NonConformanceOut(NonConformanceBase):
    id: int
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NonConformanceRequest(BaseModel):
    issue_description: str
    nonconformance_type: str = "product"  # product, process, system

class NonConformanceResponse(BaseModel):
    nonconformance_data: List[NonConformanceOut]
    mock: bool = False 