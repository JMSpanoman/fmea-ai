"""API payloads for PMS Report stored document regeneration (Document Control)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PmsReportRegenerateDocumentResponse(BaseModel):
    project_id: str
    report_mode: str = Field(description="'populated' or 'draft'")
    document_id: str
    document_key: str = Field(default="pms_report", description="Registry / document type key")
    created_new_document: bool
    updated_existing_document: bool
    previous_document_found: bool
    updated_at: Optional[str] = None
    preview_excerpt: str
    linked_maude_rows_count: int = 0
    pms_signal_count: int = 0
    scoring_summary_present: bool = False
