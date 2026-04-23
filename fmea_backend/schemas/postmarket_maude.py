"""Pydantic schemas for MAUDE / openFDA post-market ingestion API."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PostmarketIngestRequest(BaseModel):
    """
    Body for POST /postmarket/ingest.

    openFDA device/event search is built from these fields (AND-combined where provided).
    """

    device_name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description=(
            "Device hint expanded to OR groups across device.generic_name, device.brand_name, "
            "and device.openfda.device_name (injection-related terms add syringe/infusion/pump/pen synonyms)."
        ),
    )
    manufacturer_name: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional filter: device.manufacturer_d_name in openFDA.",
    )
    generic_device_type: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional filter: device.generic_name (e.g. product family / generic type).",
    )
    date_from: Optional[date] = Field(None, description="Inclusive start of date_received (FDA YYYYMMDD).")
    date_to: Optional[date] = Field(None, description="Inclusive end of date_received.")

    max_records: int = Field(
        500,
        ge=1,
        le=5000,
        description="Safety cap: stop after processing this many device-event rows (across pages).",
    )
    page_size: int = Field(
        100,
        ge=1,
        le=1000,
        description="openFDA limit parameter per request (max 1000 per openFDA docs).",
    )

    @field_validator("device_name", "manufacturer_name", "generic_device_type", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v

    @model_validator(mode="after")
    def date_order(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be on or before date_to")
        return self


class PostmarketIngestResponse(BaseModel):
    """Summary counts after an ingestion run."""

    fetched: int = Field(..., description="Raw device-level rows processed from openFDA responses.")
    inserted: int = Field(..., description="New rows written to the database.")
    skipped_duplicates: int = Field(..., description="Rows skipped because they already existed (dedup hit).")
    skipped_malformed: int = Field(
        0,
        description="Rows skipped due to parse/normalization errors (logged server-side).",
    )
    openfda_total_hint: Optional[int] = Field(
        None,
        description="openFDA meta.results.total when available (may exceed fetched due to max_records).",
    )
    warnings: List[str] = Field(default_factory=list, description="Non-fatal issues (e.g. empty search results).")
    search_query_used: str = Field(
        default="",
        description="Final openFDA ``search`` string used for pagination after strategy selection / fallback.",
    )
    query_attempts: List[str] = Field(
        default_factory=list,
        description="Each strategy attempted (label + query), newest/broadest last if fallbacks ran.",
    )
    expanded_device_terms: List[str] = Field(
        default_factory=list,
        description="Device tokens (including synonyms) OR’d inside generic/brand/openfda.device_name groups.",
    )
    sample_source_report_keys: List[str] = Field(
        default_factory=list,
        description="Sample FDA report identifiers from the first ingested page (for debugging).",
    )
