"""
API schemas for orchestrated post-market pipeline, FMEA bridge, and match reporting.

DISCLAIMER (propagate to clients):
    openFDA MAUDE data are incomplete, biased, and under-reported. Counts and scores are
    supporting surveillance context only — not incidence rates. Expert review is required
    before changing FMEA ratings or design controls.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.postmarket_risk_scoring import SuggestedMissingRisk


# --- Pipeline ---


class PostmarketRunPipelineRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    device_type: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Device search term for MAUDE corpus + scoring (generic/brand/normalized name match).",
    )
    device_name: Optional[str] = Field(
        None,
        max_length=500,
        description="If set and run_ingestion, used as openFDA device_name (else device_type).",
    )
    manufacturer_name: Optional[str] = Field(None, max_length=500)
    generic_device_type: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional openFDA generic_name filter during ingest.",
    )
    component: Optional[str] = Field(None, max_length=500)
    failure_mode: Optional[str] = Field(None, max_length=2000)
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    run_ingestion: bool = True
    run_extraction: bool = True
    run_scoring: bool = True

    max_ingest_records: int = Field(400, ge=1, le=5000)
    max_extract_events: int = Field(300, ge=1, le=2000)

    @model_validator(mode="after")
    def date_order(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self


class PostmarketScoringSummaryOut(BaseModel):
    device_type_used: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    failure_mode_themes_scored: int = 0
    suggested_missing_count: int = 0


class PostmarketRunPipelineResponse(BaseModel):
    records_fetched: int = 0
    records_inserted: int = 0
    records_skipped: int = 0
    records_extracted: int = 0
    extracted_failure_modes_count: int = 0
    scoring_summary: Optional[PostmarketScoringSummaryOut] = None
    top_missing_risks: List[SuggestedMissingRisk] = Field(default_factory=list)
    status: Literal["completed", "partial", "failed"] = "completed"
    warnings: List[str] = Field(default_factory=list)
    disclaimer: str = Field(
        default=(
            "MAUDE/openFDA narratives are noisy and under-reported; post-market frequency is supporting "
            "evidence only. Expert review is required before adopting FMEA or risk-file changes."
        )
    )
    pipeline_run_id: Optional[str] = None


# --- Match report ---


class PostmarketMatchedThemeOut(BaseModel):
    normalized_failure_mode: str
    suggested_probability_score: int
    supporting_event_count: int
    weighted_event_count: float
    matched_fmea_row_id: Optional[str] = None
    matched_fmea_failure_mode: Optional[str] = None


class PostmarketUnmatchedThemeOut(BaseModel):
    normalized_failure_mode: str
    suggested_probability_score: int
    supporting_event_count: int
    weighted_event_count: float


class PostmarketMissingRisksResponse(BaseModel):
    project_id: str
    device_type_used: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    matched_themes: List[PostmarketMatchedThemeOut] = Field(default_factory=list)
    unmatched_themes: List[PostmarketUnmatchedThemeOut] = Field(default_factory=list)
    likely_missing_risks: List[SuggestedMissingRisk] = Field(default_factory=list)
    disclaimer: str = Field(
        default=(
            "MAUDE/openFDA narratives are noisy and under-reported; post-market frequency is supporting "
            "evidence only. Expert review is required before adopting FMEA or risk-file changes."
        )
    )


# --- Add to FMEA ---


class PostmarketAddMissingRiskToFmeaRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    normalized_failure_mode: str = Field(..., min_length=1, max_length=2000)
    device_type: Optional[str] = Field(
        None,
        max_length=500,
        description="MAUDE device filter for probability heuristic; defaults from project profile when omitted.",
    )
    component: Optional[str] = Field(None, max_length=500)
    suggested_effect: Optional[str] = Field(None, max_length=4000)
    suggested_cause: Optional[str] = Field(None, max_length=4000)
    source_event_ids: Optional[List[str]] = Field(None, description="MAUDE event UUIDs supporting this theme.")

    @field_validator("normalized_failure_mode", "component", "suggested_effect", "suggested_cause", mode="before")
    @classmethod
    def strip_opt(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


class PostmarketAddMissingRiskToFmeaResponse(BaseModel):
    fmea_row_id: str
    message: str = Field(
        default="Draft FMEA row created from post-market theme — expert review required before release use."
    )
    disclaimer: str = Field(
        default=(
            "MAUDE-derived suggestions are not validated clinical hazards. Complete severity/detection "
            "and control analysis per your QMS."
        )
    )
