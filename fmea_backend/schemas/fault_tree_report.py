from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class FaultTreeReportBase(BaseModel):
    top_event: str
    fault_tree_type: str
    complexity: Optional[str] = None
    risk_level: Optional[str] = None
    root_causes: Optional[str] = None
    intermediate_events: Optional[str] = None
    basic_events: Optional[str] = None
    probability: Optional[str] = None
    cut_sets: Optional[str] = None
    minimal_cut_sets: Optional[str] = None
    risk_assessment: Optional[str] = None
    mitigation_strategies: Optional[str] = None
    responsible_party: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    analysis_method: Optional[str] = None
    fmea_link: Optional[str] = None
    regulatory_requirements: Optional[str] = None
    closure_summary: Optional[str] = None
    milestones: Optional[str] = None
    risk_controls_update: Optional[str] = None
    version: Optional[str] = "1.0"

class FaultTreeReportCreate(FaultTreeReportBase):
    project_id: int
    user_id: str

class FaultTreeReportUpdate(FaultTreeReportBase):
    pass

class FaultTreeReport(FaultTreeReportBase):
    id: int
    project_id: int
    user_id: str
    analysis_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FaultTreeReportResponse(BaseModel):
    id: int
    top_event: str
    fault_tree_type: str
    complexity: Optional[str] = None
    risk_level: Optional[str] = None
    root_causes: Optional[str] = None
    intermediate_events: Optional[str] = None
    basic_events: Optional[str] = None
    probability: Optional[str] = None
    cut_sets: Optional[str] = None
    minimal_cut_sets: Optional[str] = None
    risk_assessment: Optional[str] = None
    mitigation_strategies: Optional[str] = None
    responsible_party: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    analysis_method: Optional[str] = None
    fmea_link: Optional[str] = None
    regulatory_requirements: Optional[str] = None
    closure_summary: Optional[str] = None
    milestones: Optional[str] = None
    risk_controls_update: Optional[str] = None
    analysis_timestamp: Optional[datetime] = None
    version: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
