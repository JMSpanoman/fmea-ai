from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class CAPABase(BaseModel):
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
    effectiveness_check_plan: Optional[str] = None
    fmea_link: Optional[str] = None
    regulatory_impact: Optional[str] = None
    closure_summary: Optional[str] = None
    milestones: Optional[str] = None
    risk_controls_update: Optional[str] = None
    analysis_timestamp: Optional[datetime] = None
    version: Optional[str] = "1.0"

class CAPACreate(CAPABase):
    pass

class CAPAUpdate(CAPABase):
    pass

class CAPAOut(CAPABase):
    id: int
    project_id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 