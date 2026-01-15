from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List, Optional
import re

from sqlalchemy.orm import Session

from crud import document as document_crud
from crud import risk_item as risk_item_crud


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _doc_ref_line(project_id: str, doc: Any) -> str:
    if not doc:
        return ""
    return f"/projects/{project_id}/documents/{doc.id}"


def _safe_status(s: Optional[str]) -> str:
    return (s or "draft").strip()


def compile_submission_index(db: Session, *, project_id: str, project_name: str) -> str:
    """
    Compile-only: list documents with status/version/date and a link reference.
    No conclusions; no content generation beyond indexing.
    """
    docs = document_crud.get_documents_by_project(db, project_id)
    rows: List[str] = []
    for d in sorted(docs, key=lambda x: ((x.type or "").lower(), (x.name or "").lower(), str(x.id or ""))):
        rows.append(
            f"{d.name} | {d.type} | {_safe_status(d.status)} | v{d.version} | {d.updated_at or d.created_at} | {_doc_ref_line(project_id, d)}"
        )

    header = [
        "Submission Index — Draft (compiled)",
        "",
        "SYSTEM-GENERATED INDEX (links/status only; not assessed)",
        f"Generated at (UTC): {_now()}",
        f"Project: {project_name}",
        f"Project ID: {project_id}",
        "",
        "Index",
        "document_name | document_type | status | latest_version | last_updated | link/reference",
        "-" * 120,
    ]
    if not rows:
        rows = ["(No documents found for this project.)"]
    return "\n".join(header + rows) + "\n"


def compile_audit_package(db: Session, *, project_id: str, project_name: str) -> str:
    """
    Compile-only: list audit-relevant artifacts with status/version.
    Includes a gaps section (not started + traceability gaps hint).
    """
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    def row(label: str, t: str) -> str:
        d = by_type.get(t)
        if not d:
            return f"- {label}: (missing)"
        return f"- {label}: status={_safe_status(d.status)} version=v{d.version} link={_doc_ref_line(project_id, d)}"

    gaps: List[str] = []
    for d in docs:
        if _safe_status(d.status).lower().replace(" ", "_") in {"not_started", "not-started"}:
            gaps.append(f"- Not started: {d.type} ({d.name})")

    tm = by_type.get("traceability_matrix")
    if tm and tm.content and "GAP:" in tm.content:
        gaps.append("- Traceability gaps detected (see Traceability Matrix for details).")

    body: List[str] = [
        "Audit Package — Draft (compiled)",
        "",
        "SYSTEM-GENERATED PACKAGE VIEW (links/status only; not assessed)",
        f"Generated at (UTC): {_now()}",
        f"Project: {project_name}",
        f"Project ID: {project_id}",
        "",
        "Core Risk Docs",
        row("Risk Management Plan (RMP)", "rmp"),
        row("Hazard Analysis", "hazard_analysis"),
        row("FMEA", "fmea"),
        row("Risk Controls", "risk_controls_doc"),
        row("Residual Risk Evaluation", "residual_risk"),
        row("RMF/RMR (compiled)", "rmf"),
        "",
        "Design Controls",
        row("Design & Development Plan", "design_dev_plan"),
        row("Design Inputs", "design_inputs_doc"),
        row("Design Outputs", "design_outputs_doc"),
        row("Design Reviews", "design_reviews"),
        row("Design Change Record", "design_change_record"),
        "",
        "V&V Artifacts",
        row("V&V Plan", "vv_plan"),
        row("V&V Evidence Report", "vv_evidence"),
        row("Validation Summary", "validation_summary"),
        row("Usability Risk Analysis", "usability_risk_analysis"),
        row("Human Factors Validation", "hf_validation"),
        "",
        "Traceability & Impact",
        row("Traceability Matrix", "traceability_matrix"),
        row("Change Impact Analysis", "change_impact_analysis"),
        "",
        "Gaps (informational; no auto-fix)",
        *(gaps if gaps else ["- (No gaps detected by this compiler. This is not an assessment.)"]),
        "",
    ]
    return "\n".join(body)


def compile_essential_requirements_checklist(db: Session, *, project_id: str, project_name: str) -> str:
    """
    Compile-only checklist with Not assessed defaults.
    Does not claim coverage. Uses references only.
    """
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    ha = by_type.get("hazard_analysis")
    fmea = by_type.get("fmea")
    rcd = by_type.get("risk_controls_doc")
    di_doc = by_type.get("design_inputs_doc")
    vvp = by_type.get("vv_plan")
    vve = by_type.get("vv_evidence")

    requirement_headings = [
        "General safety and performance (placeholder heading)",
        "Risk management (placeholder heading)",
        "Information supplied with the device (placeholder heading)",
        "Software / cybersecurity (placeholder heading)",
        "Electrical safety / EMC (placeholder heading)",
        "Clinical / performance evaluation (placeholder heading)",
    ]

    risks = risk_item_crud.get_risk_items_by_project(db, project_id)
    risk_refs: List[str] = []
    for r in sorted(risks, key=lambda x: (str(getattr(x, "title", "") or "").lower(), str(getattr(x, "id", "") or "")))[:8]:
        risk_refs.append(f"{getattr(r, 'title', '')} (risk_item_id={getattr(r, 'id', '')})")

    di_refs: List[str] = []
    if di_doc and di_doc.content:
        for m in re.finditer(r"\\bDI-[A-Z0-9]+(?:-[A-Z0-9]+)*-\\d+\\b|\\bDI-\\d+\\b", di_doc.content, flags=re.IGNORECASE):
            di_refs.append(m.group(0))
        uniq: List[str] = []
        for x in di_refs:
            if x not in uniq:
                uniq.append(x)
        di_refs = uniq[:12]

    def ref(doc: Any) -> str:
        return _doc_ref_line(project_id, doc) if doc else ""

    header = [
        "Essential Requirements Checklist — Draft (compiled)",
        "",
        "SYSTEM-GENERATED CHECKLIST (links only; NOT ASSESSED)",
        f"Generated at (UTC): {_now()}",
        f"Project: {project_name}",
        f"Project ID: {project_id}",
        "",
        "Checklist (no pass/fail; status defaults to Not assessed)",
        "requirement | related_risks | related_design_inputs | evidence_refs | status",
        "-" * 120,
    ]

    evidence_refs = f"HA:{ref(ha)}; FMEA:{ref(fmea)}; RC:{ref(rcd)}; VVPlan:{ref(vvp)}; VVEvidence:{ref(vve)}"
    related_risks = ", ".join(risk_refs) if risk_refs else ""
    related_dis = ", ".join(di_refs) if di_refs else ""

    rows: List[str] = []
    for h in requirement_headings:
        rows.append(f"{h} | {related_risks} | {related_dis} | {evidence_refs} | Not assessed")

    return "\n".join(header + (rows if rows else ["(No checklist rows available.)"])) + "\n"

