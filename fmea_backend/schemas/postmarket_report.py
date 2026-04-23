"""
Structured post-market report (MAUDE / openFDA) for quality, regulatory, and risk review.

PDF_EXPORT (future):
    - Server: render this JSON with WeasyPrint / pdfkit from an HTML template, or map fields to ReportLab.
    - Client: reuse section order in ``PostMarketReport.tsx`` with print CSS (@media print) and window.print(),
      or feed the same JSON into existing jspdf + jspdf-autotable tables.

Language is intentionally non-causal: “reported events suggest”, “commonly observed in analyzed records”.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PostmarketReportRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    device_type: Optional[str] = Field(
        None,
        max_length=500,
        description="MAUDE device filter; defaults from project profile when omitted.",
    )
    device_name: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional label for report scope (display only; ingest/search uses device_type).",
    )
    component: Optional[str] = Field(None, max_length=500)
    failure_mode: Optional[str] = Field(None, max_length=2000)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    include_missing_risks: bool = True
    include_trend_summary: bool = True
    include_outcome_breakdown: bool = True
    max_failure_modes: int = Field(10, ge=1, le=50)
    max_phrase_rows: int = Field(10, ge=3, le=30)

    @model_validator(mode="after")
    def date_order(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self


class ProjectSummaryBlock(BaseModel):
    project_id: str
    project_name: str
    project_description: Optional[str] = None


class FilterSummaryBlock(BaseModel):
    device_type_used: str
    device_name_label: Optional[str] = None
    component_filter: Optional[str] = None
    failure_mode_filter: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class EvidenceSummaryBlock(BaseModel):
    total_maude_records_analyzed: int
    """NLP-linked MAUDE device-event rows matching filters (one row per extracted narrative linkage)."""
    date_range_analyzed_start: Optional[date] = None
    date_range_analyzed_end: Optional[date] = None
    qualitative_summary: str
    component_focus_note: Optional[str] = None


class PhraseCountRow(BaseModel):
    phrase: str
    count: int
    percentage_of_analyzed: Optional[float] = Field(
        None,
        description="Share of analyzed NLP-linked rows where this phrase appeared (approximate).",
    )


class OutcomeBreakdownRow(BaseModel):
    outcome: Literal["malfunction", "injury", "death", "other", "unknown"]
    count: int
    percentage: float


class TrendPeriodRow(BaseModel):
    period_label: str
    event_count: int


class TrendSummaryBlock(BaseModel):
    granularity: Literal["monthly", "quarterly"]
    periods: List[TrendPeriodRow]
    qualitative_summary: str


class ReportTopFailureModeRow(BaseModel):
    normalized_failure_mode: str
    supporting_event_count: int
    weighted_event_count: float
    top_related_components: List[PhraseCountRow]
    top_related_effects: List[PhraseCountRow]
    top_related_causes: List[PhraseCountRow]
    suggested_probability_score: Optional[int] = None
    evidence_language_note: str = Field(
        default="Commonly observed in analyzed MAUDE records for this filter; not a measured failure rate."
    )


class MissingRealWorldRiskRow(BaseModel):
    normalized_failure_mode: str
    component: Optional[str] = None
    supporting_event_count: int
    rationale: str
    add_to_fmea_available: bool = True
    requires_expert_review: bool = True


class RecommendedFmeaDraftRow(BaseModel):
    normalized_failure_mode: str
    supporting_event_count: int
    weighted_event_count: Optional[float] = None
    rationale: str
    requires_expert_review: bool = True
    add_to_fmea_available: bool = True


class PostmarketReportingPeriodBlock(BaseModel):
    """Reporting window used for aggregation (filter dates or inferred defaults)."""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    label: str = Field(
        default="",
        description="Human-readable period, e.g. '2024-01-01 to 2025-03-24 (UTC filters)'.",
    )
    markets_regions_note: Optional[str] = Field(
        default=None,
        description="Optional markets/regions when available from project metadata.",
    )


class PostmarketDataSummaryBlock(BaseModel):
    """Counts aligned with regulatory-style PMS summaries (data-backed only when report_mode=populated)."""

    maude_nlp_linked_records_reviewed: int = 0
    pms_signal_records_in_scope: int = 0
    unique_normalized_failure_modes: int = 0
    malfunction_outcome_events: int = 0
    injury_outcome_events: int = 0
    death_outcome_events: int = 0
    other_outcome_events: int = 0
    unknown_outcome_events: int = 0
    date_range_analyzed_start: Optional[date] = None
    date_range_analyzed_end: Optional[date] = None


class PostmarketTopFindingsBlock(BaseModel):
    """Condensed top themes for dashboards and document embedding."""

    top_failure_modes: List[PhraseCountRow] = Field(default_factory=list)
    top_causes: List[PhraseCountRow] = Field(default_factory=list)
    top_effects: List[PhraseCountRow] = Field(default_factory=list)
    top_components: List[PhraseCountRow] = Field(default_factory=list)
    trend_qualitative: Optional[str] = None


class PmsSignalIdentifiedRow(BaseModel):
    signal_id: str
    description: str
    source: str
    status: str
    notes: Optional[str] = None


class PostmarketReportResponse(BaseModel):
    report_mode: Literal["populated", "draft"] = Field(
        default="draft",
        description="populated when any of NLP-linked MAUDE rows, in-scope PMS signals, or pipeline scoring snapshot exists.",
    )
    report_title: str = Field(default="Post-Market Surveillance Summary (MAUDE)")
    generated_at: datetime
    project_summary: ProjectSummaryBlock
    filter_summary: FilterSummaryBlock
    reporting_period: PostmarketReportingPeriodBlock = Field(default_factory=PostmarketReportingPeriodBlock)
    summary: PostmarketDataSummaryBlock = Field(default_factory=PostmarketDataSummaryBlock)
    top_findings: PostmarketTopFindingsBlock = Field(default_factory=PostmarketTopFindingsBlock)
    signals_identified: List[PmsSignalIdentifiedRow] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    evidence_summary: EvidenceSummaryBlock
    top_failure_modes: List[ReportTopFailureModeRow]
    top_causes: List[PhraseCountRow]
    top_effects: List[PhraseCountRow]
    outcome_breakdown: List[OutcomeBreakdownRow]
    trend_summary: Optional[TrendSummaryBlock] = None
    missing_real_world_risks: List[MissingRealWorldRiskRow] = Field(default_factory=list)
    recommended_fmea_drafts: List[RecommendedFmeaDraftRow] = Field(default_factory=list)
    disclaimer: str
    future_data_sources_placeholder: str = Field(
        default=(
            "Future releases may incorporate FDA recalls, internal complaints, CAPA, and vigilance feeds "
            "using the same report structure."
        )
    )
