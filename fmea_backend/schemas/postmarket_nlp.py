"""Pydantic schemas for MAUDE narrative NLP extraction API and LLM parsing."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


OutcomeClass = Literal["malfunction", "injury", "death", "other", "unknown"]


class MaudeNarrativeLlmExtract(BaseModel):
    """
    Expected JSON shape from the LLM (all fields optional except where noted).
    Unknown / not stated in narrative → null.
    """

    failure_mode: Optional[str] = Field(None, description="What failed or behaved wrong (device/system behavior).")
    cause: Optional[str] = Field(None, description="Contributing cause if explicitly stated; not speculation.")
    effect: Optional[str] = Field(None, description="Consequence on patient, user, or device use.")
    component: Optional[str] = Field(None, description="Named part/subsystem if explicitly mentioned.")
    harm: Optional[str] = Field(None, description="Harm or potential harm if stated.")
    outcome_classification: Optional[str] = Field(
        None,
        description="One of: malfunction, injury, death, other, unknown",
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Model confidence 0–1 for this extraction overall.",
    )
    normalized_risk_phrase: Optional[str] = Field(
        None,
        description="Short canonical-style phrase summarizing the risk (no new facts).",
    )

    @field_validator(
        "failure_mode",
        "cause",
        "effect",
        "component",
        "harm",
        "normalized_risk_phrase",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v

    @field_validator("outcome_classification", mode="before")
    @classmethod
    def lower_outcome(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return v.strip().lower()
        return v


class PostmarketExtractRequest(BaseModel):
    """POST /postmarket/extract — provide exactly one of ``event_id`` or ``event_ids``."""

    event_id: Optional[str] = Field(None, description="Single MAUDE event UUID (maude_adverse_events.id).")
    event_ids: Optional[List[str]] = Field(None, description="Batch of MAUDE event UUIDs.")

    @model_validator(mode="after")
    def exactly_one_mode(self):
        has_one = bool(self.event_id and self.event_id.strip())
        has_many = bool(self.event_ids and len(self.event_ids) > 0)
        if has_one and has_many:
            raise ValueError("Provide only one of event_id or event_ids")
        if not has_one and not has_many:
            raise ValueError("Provide event_id or event_ids")
        return self

    def resolved_event_ids(self) -> List[str]:
        if self.event_id and self.event_id.strip():
            return [self.event_id.strip()]
        return [x.strip() for x in (self.event_ids or []) if x and str(x).strip()]


class EventExtractResult(BaseModel):
    event_id: str
    status: Literal["ok", "skipped_no_narrative", "error", "not_found"]
    extraction_id: Optional[str] = None
    detail: Optional[str] = None


class PostmarketExtractResponse(BaseModel):
    requested: int
    succeeded: int
    failed: int
    skipped: int
    results: List[EventExtractResult]
