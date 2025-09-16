from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class HazardAnalysisBase(BaseModel):
    hazard_description: str
    hazard_type: str
    severity: Optional[str] = None
    probability: Optional[str] = None
    risk_level: Optional[str] = None
    affected_components: Optional[str] = None
    potential_consequences: Optional[str] = None
    existing_controls: Optional[str] = None
    risk_assessment: Optional[str] = None
    mitigation_measures: Optional[str] = None
    responsible_party: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    monitoring_plan: Optional[str] = None
    fmea_link: Optional[str] = None
    regulatory_requirements: Optional[str] = None
    closure_summary: Optional[str] = None
    milestones: Optional[str] = None
    risk_controls_update: Optional[str] = None
    version: Optional[str] = "1.0"

class HazardAnalysisCreate(HazardAnalysisBase):
    project_id: int
    user_id: str

class HazardAnalysisUpdate(HazardAnalysisBase):
    pass

class HazardAnalysis(HazardAnalysisBase):
    id: int
    project_id: int
    user_id: str
    analysis_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class HazardAnalysisResponse(BaseModel):
    id: int
    hazard_description: str
    hazard_type: str
    severity: Optional[str] = None
    probability: Optional[str] = None
    risk_level: Optional[str] = None
    affected_components: Optional[str] = None
    potential_consequences: Optional[str] = None
    existing_controls: Optional[str] = None
    risk_assessment: Optional[str] = None
    mitigation_measures: Optional[str] = None
    responsible_party: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    monitoring_plan: Optional[str] = None
    fmea_link: Optional[str] = None
    regulatory_requirements: Optional[str] = None
    closure_summary: Optional[str] = None
    milestones: Optional[str] = None
    risk_controls_update: Optional[str] = None
    analysis_timestamp: Optional[datetime] = None
    version: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
