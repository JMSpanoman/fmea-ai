from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class PMSSignalBase(BaseModel):
    signal_key: str
    signal_type: str  # complaint | field_data | trend | service | literature
    component_names_json: List[str]
    title: str
    description: Optional[str] = None
    source_ref: Optional[str] = None
    date_detected: datetime
    severity_observed: Optional[int] = None
    frequency_observed: Optional[int] = None
    rate_observed: Optional[float] = None
    trend_status: str = "under_review"  # none | under_review | confirmed | false_alarm
    trigger_status: str = "not_triggered"  # not_triggered | risk_review_required | capa_required | change_required
    recommended_action: Optional[str] = None
    owner: Optional[str] = None
    status: str = "open"  # open | investigating | closed

class PMSSignalCreate(PMSSignalBase):
    pass

class PMSSignalUpdate(BaseModel):
    signal_key: Optional[str] = None
    signal_type: Optional[str] = None
    component_names_json: Optional[List[str]] = None
    title: Optional[str] = None
    description: Optional[str] = None
    source_ref: Optional[str] = None
    date_detected: Optional[datetime] = None
    severity_observed: Optional[int] = None
    frequency_observed: Optional[int] = None
    rate_observed: Optional[float] = None
    trend_status: Optional[str] = None
    trigger_status: Optional[str] = None
    recommended_action: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None

class PMSSignalOut(PMSSignalBase):
    id: str
    project_id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PMSSignalLinkRiskRequest(BaseModel):
    risk_item_id: str
    link_type: str = "impacts"

class PMSSignalHandoffCAPARequest(BaseModel):
    capa_title: Optional[str] = None
    capa_description: Optional[str] = None

class PMSSignalHandoffChangeRequest(BaseModel):
    change_title: Optional[str] = None
    change_description: Optional[str] = None

class PMSSignalReportGenerateRequest(BaseModel):
    components: Optional[List[Dict[str, str]]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    include_open_only: bool = False
    include_traceability: bool = True
    include_actions: bool = True
    format: str = "html"

