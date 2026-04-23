"""
Pydantic schemas for post-market → FMEA probability suggestion scoring.

IMPORTANT (regulatory / scientific):
    MAUDE-derived frequencies are **supporting surveillance evidence only**. They reflect
    reporter narratives and FDA MAUDE selection biases — **not** true device incidence rates.
    Probability suggestions must be reviewed in clinical / QMS context before updating FMEA.
"""
from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


RecentTrend = Literal["stable", "increasing", "decreasing", "insufficient_data"]

ConfidenceLevel = Literal["low", "medium", "high"]


class OutcomeWeights(BaseModel):
    """Multipliers applied per event row before aggregation (tunable)."""

    death: float = Field(5.0, ge=0)
    injury: float = Field(3.0, ge=0)
    malfunction: float = Field(1.0, ge=0)
    other: float = Field(1.5, ge=0)
    unknown: float = Field(1.2, ge=0)


class ProbabilityBandThresholds(BaseModel):
    """
    Map **weighted** event totals (sum of outcome weights in the window) to FMEA probability **1–5**.

    Let ``W`` = weighted total. Monotonic bands:
    - **Score 1**: ``W < min_weighted_for_2``  (tune how “strict” score 1 is by raising/lowering this)
    - **Score 2**: ``min_weighted_for_2 <= W < min_weighted_for_3``
    - **Score 3**: ``min_weighted_for_3 <= W < min_weighted_for_4``
    - **Score 4**: ``min_weighted_for_4 <= W < min_weighted_for_5``
    - **Score 5**: ``W >= min_weighted_for_5``
    """

    min_weighted_for_2: float = Field(3.0, ge=0)
    min_weighted_for_3: float = Field(10.0, ge=0)
    min_weighted_for_4: float = Field(25.0, ge=0)
    min_weighted_for_5: float = Field(60.0, ge=0)


class TrendDetectionConfig(BaseModel):
    """Heuristic split-window trend on raw event counts."""

    increasing_ratio: float = Field(1.25, ge=1.0, description="late/early ≥ this → increasing")
    decreasing_ratio: float = Field(0.75, gt=0, le=1.0, description="late/early ≤ this → decreasing")
    min_events_per_half: int = Field(3, ge=0, description="Minimum counts in each half to claim trend")


class PostmarketRiskScoringConfig(BaseModel):
    """Full tunable config (defaults suitable for demos; calibrate per product class)."""

    outcome_weights: OutcomeWeights = Field(default_factory=OutcomeWeights)
    probability_thresholds: ProbabilityBandThresholds = Field(default_factory=ProbabilityBandThresholds)
    trend: TrendDetectionConfig = Field(default_factory=TrendDetectionConfig)
    max_failure_modes_returned: int = Field(40, ge=1, le=200)
    default_lookback_years: int = Field(5, ge=1, le=30)


class FailureModeScoreRequest(BaseModel):
    device_type: str = Field(..., min_length=1, max_length=500, description="Matched against MAUDE generic/brand/normalized device fields.")
    component: Optional[str] = Field(None, max_length=500)
    failure_mode: str = Field(..., min_length=1, max_length=2000, description="Matched against NLP failure_mode / normalized_risk_phrase.")
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    @field_validator("device_type", "component", "failure_mode", mode="before")
    @classmethod
    def strip(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v

    @model_validator(mode="after")
    def date_order(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self


class RelatedPhraseCount(BaseModel):
    phrase: str
    count: int


class FailureModeScoreResponse(BaseModel):
    suggested_probability_score: int = Field(..., ge=1, le=5)
    supporting_event_count: int = Field(..., ge=0)
    weighted_event_count: float = Field(..., ge=0)
    recent_trend: RecentTrend
    confidence_level: ConfidenceLevel
    rationale: str
    top_related_effects: List[RelatedPhraseCount]
    top_related_causes: List[RelatedPhraseCount]
    device_type: str
    component_filter: Optional[str] = None
    failure_mode_query: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class ProjectRiskScoreItem(BaseModel):
    normalized_failure_mode: str
    suggested_probability_score: int = Field(..., ge=1, le=5)
    supporting_event_count: int
    weighted_event_count: float
    recent_trend: RecentTrend
    confidence_level: ConfidenceLevel
    rationale: str
    top_related_effects: List[RelatedPhraseCount]
    top_related_causes: List[RelatedPhraseCount]
    top_components: List[RelatedPhraseCount] = Field(default_factory=list)


class SuggestedMissingRisk(BaseModel):
    """Post-market theme with no strong match in project FMEA / project risk items."""

    failure_mode_hint: str
    weighted_event_count: float
    supporting_event_count: int
    rationale: str


class DeviceFamilyAggregate(BaseModel):
    """Roll-up of NLP-linked events by MAUDE device family fields (generic / normalized / brand)."""

    device_family: str
    supporting_event_count: int
    weighted_event_count: float


class ComponentAggregate(BaseModel):
    """Roll-up by NLP-extracted ``component`` text (post-market themes)."""

    component_text: str
    supporting_event_count: int
    weighted_event_count: float


class ProjectRiskScoreResponse(BaseModel):
    project_id: str
    device_type_used: str
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    config_snapshot: PostmarketRiskScoringConfig
    device_family_aggregates: List[DeviceFamilyAggregate] = Field(
        default_factory=list,
        description="Counts/weights grouped by openFDA-style device family string on the parent MAUDE row.",
    )
    component_aggregates: List[ComponentAggregate] = Field(
        default_factory=list,
        description="Counts/weights grouped by extracted component mentions across the filtered corpus.",
    )
    items: List[ProjectRiskScoreItem]
    suggested_missing_risks: List[SuggestedMissingRisk]
