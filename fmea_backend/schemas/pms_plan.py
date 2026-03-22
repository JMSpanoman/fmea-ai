"""PMS Plan Generator API schemas (FMEA + MAUDE-like signals + AI)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PmsPlanGenerateRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    device_name: str = Field(..., min_length=1)
    intended_use: str = Field(..., min_length=1)


class MaudeSignalPublic(BaseModel):
    model_config = ConfigDict(extra="allow")

    failure_mode: str
    event_count: int
    trend: str
    severity: str
    source: Optional[str] = None
    notes: Optional[str] = None
    recommended_monitoring_focus: Optional[str] = None


class PmsPlanSections(BaseModel):
    """Structured PMS plan body (ISO 14971 / FDA-oriented narrative sections)."""

    device_overview: str
    pms_objectives: str
    data_sources: str
    maude_analysis: str
    risk_mapping: str
    signal_detection: str
    pms_activities: str
    capa_integration: str
    benefit_risk: str
    reporting: str


class PmsPlanGenerateResponse(PmsPlanSections):
    """Response from POST /pms/generate (matches persisted record + audit metadata)."""

    generation_id: str
    project_id: str
    created_at: datetime
    maude_signals: List[MaudeSignalPublic]
    fmea_row_count: int
    model: Optional[str] = None
    ai_generated: bool = False
    summary: str = ""
    status: str = "draft"
    version: int = 1
    warning: Optional[str] = None


class PmsPlanHistoryItem(BaseModel):
    """One saved or legacy-audited PMS plan."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: str
    project_id: str
    device_name: Optional[str] = None
    intended_use: Optional[str] = None
    created_at: datetime
    input_summary: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = "draft"
    version: Optional[int] = None
    plan: PmsPlanSections
    maude_signals: List[MaudeSignalPublic] = Field(default_factory=list)
    fmea_row_count: Optional[int] = None
    model: Optional[str] = None
    warning: Optional[str] = None
    ai_generated: Optional[bool] = None


class PmsPlanHistoryListResponse(BaseModel):
    project_id: str
    items: List[PmsPlanHistoryItem]
