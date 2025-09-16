from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class FMEABase(BaseModel):
    component: str
    function_description: Optional[str] = None
    potential_failure_mode: Optional[str] = None
    potential_effects: Optional[str] = None
    severity: Optional[int] = None
    potential_causes: Optional[str] = None
    occurrence: Optional[int] = None
    current_controls: Optional[str] = None
    detection: Optional[int] = None
    risk_priority_number: Optional[int] = None
    recommended_actions: Optional[str] = None
    responsible_party: Optional[str] = None
    target_completion_date: Optional[date] = None
    actions_taken: Optional[str] = None
    final_severity: Optional[int] = None
    final_occurrence: Optional[int] = None
    final_detection: Optional[int] = None
    final_risk_priority_number: Optional[int] = None

class FMEACreate(FMEABase):
    pass

class FMEAUpdate(BaseModel):
    component: Optional[str] = None
    function_description: Optional[str] = None
    potential_failure_mode: Optional[str] = None
    potential_effects: Optional[str] = None
    severity: Optional[int] = None
    potential_causes: Optional[str] = None
    occurrence: Optional[int] = None
    current_controls: Optional[str] = None
    detection: Optional[int] = None
    risk_priority_number: Optional[int] = None
    recommended_actions: Optional[str] = None
    responsible_party: Optional[str] = None
    target_completion_date: Optional[date] = None
    actions_taken: Optional[str] = None
    final_severity: Optional[int] = None
    final_occurrence: Optional[int] = None
    final_detection: Optional[int] = None
    final_risk_priority_number: Optional[int] = None

class FMEAOut(FMEABase):
    id: int
    project_id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AISuggestionRequest(BaseModel):
    component: str
    potential_failure_mode: Optional[str] = None
    potential_effects: Optional[str] = None
    potential_causes: Optional[str] = None
    context: Optional[str] = None 