from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChangeControlCreate(BaseModel):
    change_description: str
    initiator: str
    date_initiated: str
    status: str
    impact_assessment: Optional[str] = None
    actions_required: Optional[str] = None
    action_owner: Optional[str] = None
    due_date: Optional[str] = None
    closure_summary: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    version: Optional[str] = "1.0"

class ChangeControlUpdate(BaseModel):
    change_description: Optional[str] = None
    initiator: Optional[str] = None
    date_initiated: Optional[str] = None
    status: Optional[str] = None
    impact_assessment: Optional[str] = None
    actions_required: Optional[str] = None
    action_owner: Optional[str] = None
    due_date: Optional[str] = None
    closure_summary: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    version: Optional[str] = None

class ChangeControlOut(BaseModel):
    id: int
    project_id: int
    user_id: str
    change_description: str
    initiator: str
    date_initiated: str
    status: str
    impact_assessment: Optional[str] = None
    actions_required: Optional[str] = None
    action_owner: Optional[str] = None
    due_date: Optional[str] = None
    closure_summary: Optional[str] = None
    analysis_timestamp: Optional[str] = None
    version: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 