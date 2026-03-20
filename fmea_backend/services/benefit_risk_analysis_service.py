from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

# Canonical human-facing phrase for indeterminate / incomplete residual-risk conclusions
CANONICAL_NOT_FULLY_EVALUABLE = "Not fully evaluable"


class BenefitRiskApprovedModeBlocked(Exception):
    """Raised when approved-mode generation cannot proceed due to unresolved blockers."""

    def __init__(self, blockers: List[str]):
        self.blockers = list(blockers)
        super().__init__("Benefit–risk report cannot be issued in approved mode until blockers are resolved.")


def _safe_excerpt(text: Optional[str], max_len: int = 600) -> str:
    if not text:
        return ""
    normalized = " ".join(str(text).split())
    return normalized[:max_len]


def _norm_acceptability(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if not raw or raw == "unknown":
        return "unknown"
    if "unacceptable" in raw:
        return "unacceptable"
    if "benefit" in raw or "needs_benefit_risk" in raw:
        return "needs_benefit_risk"
    if "justification" in raw:
        return "acceptable_with_justification"
    if "acceptable" in raw:
        return "acceptable"
    return "unknown"


def _canonical_final_determination_display(raw: str) -> str:
    """Map NOT EVALUABLE / NOT FULLY EVALUABLE to one consistent phrase; keep other determinations explicit."""
    r = (raw or "").strip().upper()
    if r in {"NOT EVALUABLE", "NOT FULLY EVALUABLE"}:
        return CANONICAL_NOT_FULLY_EVALUABLE
    if not r:
        return CANONICAL_NOT_FULLY_EVALUABLE
    return str(raw).strip()


def _dedupe_top_risks(rows: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    sorted_rows = sorted(
        rows,
        key=lambda r: (r.get("residual_risk_score") if isinstance(r.get("residual_risk_score"), (int, float)) else -1),
        reverse=True,
    )
    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for r in sorted_rows:
        key = str(r.get("risk_key") or r.get("risk_item_id") or "").strip().lower()
        if not key:
            key = f"anon-{len(out)}"
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out


def _build_project_context(
    db: Session,
    *,
    project_id: str,
    project_name: str,
    version_scope: str,
) -> Dict[str, Any]:
    from crud import document as document_crud
    from models.project_profile import ProjectProfile
    from business_logic import residual_risk_builder

    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    residual = residual_risk_builder.build_residual_risk_evidence(
        db=db,
        project_id=project_id,
        component_filter=None,
        version_scope=version_scope or "approved_only",
        include_unapproved=False,
        acceptability_profile="default_med_device",
        custom_thresholds=None,
    )

    rows: List[Dict[str, Any]] = residual.get("rows") or []
    top_rows = _dedupe_top_risks(rows, limit=5)
    counts = residual.get("counts") or {}

    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}
    linked_snippets = {
        "rmp": _safe_excerpt(getattr(by_type.get("rmp"), "content", None)),
        "hazard_analysis": _safe_excerpt(getattr(by_type.get("hazard_analysis"), "content", None)),
        "residual_risk": _safe_excerpt(getattr(by_type.get("residual_risk"), "content", None)),
        "risk_controls_doc": _safe_excerpt(getattr(by_type.get("risk_controls_doc"), "content", None)),
    }
    linked_docs = {
        "residual_risk": {
            "id": getattr(by_type.get("residual_risk"), "id", None),
            "status": getattr(by_type.get("residual_risk"), "status", None),
            "version": getattr(by_type.get("residual_risk"), "version", None),
        },
        "clinical_evaluation": {
            "id": getattr(by_type.get("clinical_evaluation"), "id", None),
            "status": getattr(by_type.get("clinical_evaluation"), "status", None),
            "version": getattr(by_type.get("clinical_evaluation"), "version", None),
        },
        "hazard_analysis": {
            "id": getattr(by_type.get("hazard_analysis"), "id", None),
            "status": getattr(by_type.get("hazard_analysis"), "status", None),
            "version": getattr(by_type.get("hazard_analysis"), "version", None),
        },
        "risk_controls_doc": {
            "id": getattr(by_type.get("risk_controls_doc"), "id", None),
            "status": getattr(by_type.get("risk_controls_doc"), "status", None),
            "version": getattr(by_type.get("risk_controls_doc"), "version", None),
        },
    }

    return {
        "project_id": project_id,
        "project_name": project_name,
        "version_scope": version_scope or "approved_only",
        "residual_meta": {
            "excluded_versions": counts.get("excluded_versions"),
            "versions_included": counts.get("versions_included"),
        },
        "profile": {
            "device_description": getattr(profile, "device_description", None),
            "intended_use": getattr(profile, "intended_use", None),
            "user_population": getattr(profile, "user_population", None),
            "use_environment": getattr(profile, "use_environment", None),
            "clinical_benefit": getattr(profile, "clinical_benefit", None),
            "device_class": getattr(profile, "device_class", None),
            "implantable": getattr(profile, "implantable", None),
            "life_sustaining": getattr(profile, "life_sustaining", None),
        },
        "residual_summary": {
            "final_determination": residual.get("finalDetermination"),
            "data_quality_status": residual.get("dataQualityStatus"),
            "total_risk_items": residual.get("totalRiskItems"),
            "total_hazards": residual.get("totalHazards"),
            "benefit_risk_required_count": residual.get("benefitRiskRequiredCount"),
            "unacceptable_residual_risk_count": residual.get("unacceptableResidualRiskCount"),
        },
        "top_residual_risks": [
            {
                "risk_key": r.get("risk_key"),
                "hazard": r.get("hazard"),
                "hazardous_situation": r.get("hazardous_situation"),
                "harm": r.get("harm"),
                "residual_severity": r.get("residual_severity"),
                "residual_probability": r.get("residual_probability_of_harm"),
                "residual_risk_level": r.get("residual_risk_level"),
                "residual_risk_score": r.get("residual_risk_score"),
                "acceptability": r.get("residual_acceptability"),
                "controls_summary": r.get("controls_summary"),
            }
            for r in top_rows
        ],
        "rows": rows,
        "missing_field_counts": residual.get("missingFieldCounts") or {},
        "data_quality_status": residual.get("dataQualityStatus"),
        "final_determination": residual.get("finalDetermination"),
        "traceability_summary": residual.get("traceabilitySummary") or {},
        "risk_reduction_summary": residual.get("riskReductionSummary") or {},
        "linked_doc_snippets": linked_snippets,
        "linked_docs": linked_docs,
    }


def _scope_empty_interpretation(context: Dict[str, Any]) -> Tuple[str, str]:
    """When total residual rows are zero: interpretation + scope reason."""
    summary = context.get("residual_summary") or {}
    linked = context.get("linked_docs") or {}
    meta = context.get("residual_meta") or {}
    total = int(summary.get("total_risk_items") or 0)
    if total > 0:
        return "", ""

    rr = linked.get("residual_risk") or {}
    rr_status = str(rr.get("status") or "").lower()
    excluded = meta.get("excluded_versions")
    interpretation = "No residual-risk rows were available in the selected scope."

    parts: List[str] = []
    if rr.get("id") and rr_status and rr_status != "approved":
        parts.append(f"the linked Residual Risk Evaluation document is not approved (status: {rr.get('status')})")
    parts.append("only approved risk-item versions are included for this report (include_unapproved=false)")
    if excluded is not None and int(excluded) > 0:
        parts.append(f"{int(excluded)} risk item version(s) were excluded by scope (typically unapproved versions)")
    scope_reason = (
        "Scope reason: " + "; ".join(parts) + "."
        if parts
        else "Scope reason: no approved in-scope risk-item versions matched the selected criteria."
    )
    return interpretation, scope_reason


def _data_quality_empty_interpretation(dqs: str) -> str:
    if (dqs or "").upper() == "EMPTY":
        return "Interpretation: No usable residual-risk records were found for the selected scope."
    return ""


def _project_evidence_banner(context: Dict[str, Any], *, approved_mode: bool) -> str:
    profile = context.get("profile") or {}
    summary = context.get("residual_summary") or {}
    top = context.get("top_residual_risks") or []
    rows = context.get("rows") or []
    total = int(summary.get("total_risk_items") or 0)
    raw_det = str(summary.get("final_determination") or context.get("final_determination") or "")
    display_det = _canonical_final_determination_display(raw_det)

    lines: List[str] = []
    for r in top[:3]:
        lines.append(
            f"- {r.get('risk_key') or 'N/A'} | {r.get('hazard') or 'N/A'} | "
            f"residual={r.get('residual_risk_level') or 'N/A'} ({r.get('residual_risk_score') or 'N/A'})"
        )

    intro = (
        "PROJECT-LINKED EVIDENCE SUMMARY\n"
        "This report is compiled from structured project data (residual risk evidence, linked documents, profile).\n"
    )
    if approved_mode:
        intro = (
            "PROJECT-LINKED EVIDENCE SUMMARY\n"
            "Formal regulatory output: structured project data only; no draft helper or AI narrative is included.\n"
        )

    banner = (
        intro
        + f"- Project: {context.get('project_name')} ({context.get('project_id')})\n"
        f"- Device: {profile.get('device_description') or 'Not provided'}\n"
        f"- Intended use: {profile.get('intended_use') or 'Not provided'}\n"
        f"- Overall residual-risk conclusion (canonical): {display_det}\n"
        f"- Total residual risks (in scope): {total}\n"
        f"- Benefit-risk required count (from threshold rules): {summary.get('benefit_risk_required_count') or 0}\n"
    )
    if total == 0:
        interp, scope_r = _scope_empty_interpretation(context)
        banner += f"- Interpretation: {interp}\n- {scope_r}\n"

    banner += "Top residual risks used for context:\n"
    banner += f"{chr(10).join(lines) if lines else '- none (no rows in scope)'}\n"
    banner += "-" * 72 + "\n"
    return banner


def _build_not_fully_evaluable_reasons(
    context: Dict[str, Any],
    *,
    decision_text: Optional[str],
    rationale_text: Optional[str],
    approval_metadata: Optional[Dict[str, Any]],
) -> List[str]:
    reasons: List[str] = []
    missing = context.get("missing_field_counts") or {}
    linked = context.get("linked_docs") or {}
    profile = context.get("profile") or {}
    rows = context.get("rows") or []
    data_quality = str(context.get("data_quality_status") or "UNKNOWN")
    summary = context.get("residual_summary") or {}

    if data_quality in {"EMPTY", "INSUFFICIENT_FOR_EVALUATION", "PARTIAL"}:
        reasons.append(f"Data quality status: {data_quality}.")
    if int(missing.get("residual_severity", 0) or 0) > 0:
        reasons.append(f"Residual severity missing in {missing.get('residual_severity')} risk record(s).")
    if int(missing.get("residual_probability", 0) or 0) > 0:
        reasons.append(f"Residual probability missing in {missing.get('residual_probability')} risk record(s).")
    if int(missing.get("acceptability_decision", 0) or 0) > 0:
        reasons.append(
            f"Residual acceptability decision missing/inferred in {missing.get('acceptability_decision')} risk record(s)."
        )
    residual_doc = linked.get("residual_risk") or {}
    if not residual_doc.get("id"):
        reasons.append("No linked residual risk evaluation document found.")
    elif str(residual_doc.get("status") or "").lower() != "approved":
        reasons.append("Linked residual risk evaluation document is not approved.")
    cer = linked.get("clinical_evaluation") or {}
    if not cer.get("id"):
        reasons.append("No linked clinical evaluation document found.")
    elif str(cer.get("status") or "").lower() != "approved":
        reasons.append("Linked clinical evaluation document is not approved.")
    if not str(profile.get("clinical_benefit") or "").strip():
        reasons.append("Clinical benefit statement is missing in project profile.")
    if int(summary.get("total_risk_items") or 0) == 0 or len(rows) == 0:
        reasons.append("No residual risk rows available in selected version scope.")
    if not str(decision_text or "").strip():
        reasons.append("Overall benefit-risk decision is not populated.")
    if not str(rationale_text or "").strip():
        reasons.append("Overall decision rationale is not populated.")
    md = approval_metadata or {}
    if not str(md.get("author") or "").strip():
        reasons.append("Approval metadata missing: author.")
    if not str(md.get("reviewer") or "").strip():
        reasons.append("Approval metadata missing: reviewer.")
    if not str(md.get("approver") or "").strip():
        reasons.append("Approval metadata missing: approver.")
    if not str(md.get("date") or "").strip():
        reasons.append("Approval metadata missing: date.")
    if not str(md.get("version") or "").strip():
        reasons.append("Approval metadata missing: version.")
    if not str(md.get("issuance_state") or "").strip():
        reasons.append("Approval metadata missing: approval/issuance state.")
    return reasons


def _approved_mode_blockers(
    context: Dict[str, Any],
    *,
    decision_text: Optional[str],
    rationale_text: Optional[str],
    approval_metadata: Optional[Dict[str, Any]],
) -> List[str]:
    """Blockers that must be absent for approved-mode issuance."""
    blockers = list(
        _build_not_fully_evaluable_reasons(
            context,
            decision_text=decision_text,
            rationale_text=rationale_text,
            approval_metadata=approval_metadata,
        )
    )
    rows = context.get("rows") or []
    missing = context.get("missing_field_counts") or {}
    norm = [_norm_acceptability(r.get("residual_acceptability")) for r in rows]
    if any(n == "unknown" for n in norm):
        blockers.append("One or more in-scope risks have unknown acceptability; resolve before approved issuance.")
    if int(missing.get("linked_controls", 0) or 0) > 0:
        blockers.append("Some residual risks do not have linked controls.")
    # De-duplicate while preserving order
    seen: set[str] = set()
    out: List[str] = []
    for b in blockers:
        if b not in seen:
            seen.add(b)
            out.append(b)
    return out


def _decision_confidence(
    *,
    total: int,
    data_quality: str,
    unknown: int,
    linked_rr_ok: bool,
    linked_cer_ok: bool,
) -> str:
    if total == 0 or (data_quality or "").upper() == "EMPTY":
        return "low"
    if unknown > 0 or not linked_rr_ok or not linked_cer_ok:
        return "low"
    if (data_quality or "").upper() != "COMPLETE":
        return "medium"
    return "high"


def _build_report_scope_section(context: Dict[str, Any], *, approved_mode: bool) -> str:
    vs = context.get("version_scope") or "approved_only"
    meta = context.get("residual_meta") or {}
    linked = context.get("linked_docs") or {}
    rr = linked.get("residual_risk") or {}
    cer = linked.get("clinical_evaluation") or {}

    vs_human = {
        "approved_only": "Approved risk-item versions only (unapproved versions excluded unless project policy changes).",
        "current": "Current risk-item versions only.",
        "all": "All risk-item versions (approved and unapproved) — not used for this generator path by default.",
    }.get(vs, vs.replace("_", " "))

    approved_only_text = "Yes"
    draft_inclusion = "Excluded"
    if not approved_mode:
        approved_only_text = "Yes (default) for this generator; configurable in generation options."
        draft_inclusion = "Reported in linkage metadata only"
    return f"""## Report scope and inclusion
- Selected version scope: {vs_human}
- Draft linked documents included as evidence rows: {draft_inclusion}
- Approved residual-risk rows only: {approved_only_text}
- Versions included: {meta.get("versions_included", "N/A")}
- Versions excluded by scope: {meta.get("excluded_versions", "N/A")}
- Why rows may be absent: related project documents may exist while in-scope approved residual-risk rows are absent.
- Linked residual risk evaluation: id={rr.get("id") or "none"}, status={rr.get("status") or "none"}
- Linked clinical evaluation: id={cer.get("id") or "none"}, status={cer.get("status") or "none"}
"""


def _build_decision_grade_report(
    context: Dict[str, Any],
    *,
    approved_mode: bool = False,
    decision_text: Optional[str] = None,
    rationale_text: Optional[str] = None,
    approval_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    profile = context.get("profile") or {}
    summary = context.get("residual_summary") or {}
    rows = context.get("rows") or []
    top = context.get("top_residual_risks") or []
    linked = context.get("linked_docs") or {}
    missing = context.get("missing_field_counts") or {}
    trace = context.get("traceability_summary") or {}
    rr = context.get("risk_reduction_summary") or {}
    dqs = str(context.get("data_quality_status") or "UNKNOWN")

    total = int(summary.get("total_risk_items") or 0)
    norm = [_norm_acceptability(r.get("residual_acceptability")) for r in rows]
    acceptable = sum(1 for n in norm if n == "acceptable")
    acceptable_with_just = sum(1 for n in norm if n == "acceptable_with_justification")
    needs_br = sum(1 for n in norm if n == "needs_benefit_risk")
    unacceptable = sum(1 for n in norm if n == "unacceptable")
    unknown = sum(1 for n in norm if n == "unknown")

    highest_sev = max([int(r.get("residual_severity")) for r in rows if isinstance(r.get("residual_severity"), int)], default=None)
    highest_risk = max([int(r.get("residual_risk_score")) for r in rows if isinstance(r.get("residual_risk_score"), int)], default=None)

    screened = total
    above_threshold = sum(
        1 for r in rows if isinstance(r.get("residual_risk_score"), int) and int(r.get("residual_risk_score")) >= 20
    )
    requiring_explicit = needs_br + unacceptable
    threshold_rule = (
        "Count `requiring_explicit` = rows with inferred/stored acceptability in {needs_benefit_risk, unacceptable}; "
        "`above_threshold` = residual risk score ≥ 20. Reported `benefitRiskRequiredCount` comes from the residual "
        "risk evaluation engine for the same scope."
    )

    raw_final = str(context.get("final_determination") or summary.get("final_determination") or "")
    display_final = _canonical_final_determination_display(raw_final)
    rf_up = raw_final.strip().upper()

    reasons_not_eval = _build_not_fully_evaluable_reasons(
        context,
        decision_text=decision_text,
        rationale_text=rationale_text,
        approval_metadata=approval_metadata,
    )
    # Align overall B-R decision with machine determination and row-level signals
    if rf_up in {"NOT EVALUABLE", "NOT FULLY EVALUABLE"}:
        decision = CANONICAL_NOT_FULLY_EVALUABLE
    elif unacceptable > 0:
        decision = "Not Acceptable"
    elif needs_br > 0 or rf_up == "BENEFIT-RISK REVIEW REQUIRED":
        decision = "Acceptable with Conditions"
    elif total > 0 and acceptable + acceptable_with_just == total and (dqs or "").upper() == "COMPLETE":
        decision = "Acceptable"
    elif rf_up in {"ACCEPTABLE WITH CONDITIONS"}:
        decision = "Acceptable with Conditions"
    elif rf_up == "ACCEPTABLE":
        decision = "Acceptable"
    else:
        decision = CANONICAL_NOT_FULLY_EVALUABLE if total == 0 else "Acceptable with Conditions"

    rr_doc = linked.get("residual_risk") or {}
    cer_doc = linked.get("clinical_evaluation") or {}
    linked_rr_ok = bool(rr_doc.get("id")) and str(rr_doc.get("status") or "").lower() == "approved"
    linked_cer_ok = bool(cer_doc.get("id")) and str(cer_doc.get("status") or "").lower() == "approved"

    confidence = _decision_confidence(
        total=total,
        data_quality=dqs,
        unknown=unknown,
        linked_rr_ok=linked_rr_ok,
        linked_cer_ok=linked_cer_ok,
    )

    controls_linked = sum(1 for r in rows if r.get("has_linked_controls"))
    controls_missing = max(total - controls_linked, 0)

    top_table_lines: List[str] = []
    for r in top:
        top_table_lines.append(
            f"| {r.get('risk_key') or ''} | {r.get('hazard') or ''} | {r.get('harm') or ''} | "
            f"{r.get('residual_severity') if r.get('residual_severity') is not None else ''} | "
            f"{r.get('residual_probability') if r.get('residual_probability') is not None else ''} | "
            f"{r.get('residual_risk_level') or ''} | {r.get('residual_risk_score') if r.get('residual_risk_score') is not None else ''} | "
            f"{r.get('acceptability') or ''} |"
        )

    if top_table_lines:
        top_table_md = "\n".join(top_table_lines)
        top_risks_section = (
            "### Top residual risks (distinct)\n"
            "| Risk ID | Hazard | Harm | Residual Severity | Residual Probability | Residual Level | Residual Score | Acceptability |\n"
            "|---|---|---|---:|---:|---|---:|---|\n"
            f"{top_table_md}\n"
        )
    else:
        top_risks_section = (
            "### Top residual risks (distinct)\n"
            "*No rows in scope — no table generated. Related documents may still exist in draft or rows may be excluded "
            "because only approved in-scope versions are included.*\n"
        )

    elevated = [r for r in rows if _norm_acceptability(r.get("residual_acceptability")) in {"needs_benefit_risk", "unacceptable"}]
    elevated_lines: List[str] = []
    for r in elevated[:10]:
        elevated_lines.append(
            f"""### Risk {r.get("risk_key") or "N/A"}
- Hazard: {r.get("hazard") or "N/A"}
- Harm: {r.get("harm") or "N/A"}
- Residual severity: {r.get("residual_severity") or "N/A"}
- Residual probability: {r.get("residual_probability_of_harm") or "N/A"}
- Residual risk level/score: {r.get("residual_risk_level") or "N/A"} / {r.get("residual_risk_score") or "N/A"}
- Why further reduction is not feasible: Not yet documented in linked risk records; complete before approval.
- Benefit that may outweigh risk: {profile.get("clinical_benefit") or "Clinical benefit evidence not linked."}
- Supporting evidence: ResidualRiskDoc={linked.get("residual_risk", {}).get("id") or "missing"}, CER={linked.get("clinical_evaluation", {}).get("id") or "missing"}
- Team justification: Pending documented multidisciplinary review.
"""
        )
    elevated_md = (
        "\n".join(elevated_lines)
        if elevated_lines
        else (
            "No residual risks in the selected scope were available for classification as needs_benefit_risk or unacceptable."
        )
    )

    trace_rows: List[str] = []
    for r in top[:5]:
        trace_rows.append(
            f"| {r.get('risk_key') or ''} | {r.get('hazard') or ''} | "
            f"{linked.get('hazard_analysis', {}).get('id') or ''} | "
            f"{linked.get('residual_risk', {}).get('id') or ''} | "
            f"{linked.get('clinical_evaluation', {}).get('id') or ''} |"
        )
    if trace_rows:
        trace_section = (
            "| Risk ID | Hazard | Hazard Analysis Ref | Residual Risk Ref | Clinical Evidence Ref |\n"
            "|---|---|---|---|---|\n"
            f"{chr(10).join(trace_rows)}\n"
        )
    else:
        trace_section = (
            "*No risk-level trace rows in scope — table omitted.*\n\n"
            "**Linked document references (project):**\n"
            f"- Hazard Analysis: id={linked.get('hazard_analysis', {}).get('id') or 'none'}, status={linked.get('hazard_analysis', {}).get('status') or 'none'}\n"
            f"- Residual Risk Evaluation: id={linked.get('residual_risk', {}).get('id') or 'none'}, status={linked.get('residual_risk', {}).get('status') or 'none'}\n"
            f"- Clinical Evaluation: id={linked.get('clinical_evaluation', {}).get('id') or 'none'}, status={linked.get('clinical_evaluation', {}).get('status') or 'none'}\n"
            f"- Risk Control Measures: id={linked.get('risk_controls_doc', {}).get('id') or 'none'}, status={linked.get('risk_controls_doc', {}).get('status') or 'none'}\n"
        )

    approved_blockers = _approved_mode_blockers(
        context,
        decision_text=decision_text,
        rationale_text=rationale_text,
        approval_metadata=approval_metadata,
    )
    if unknown > 0 and "unknown acceptability" not in " ".join(approved_blockers).lower():
        approved_blockers.append("Some residual risks have unknown acceptability.")
    approved_text = "PASS" if not approved_blockers else "BLOCKED"

    dq_extra = _data_quality_empty_interpretation(dqs)

    draft_notes = ""
    if not approved_mode:
        draft_notes = "- Draft report: explanatory notes for missing data and scope are included for team review.\n"

    section10_title = "## 15. Revision history" if approved_mode else "## 15. Revision history"
    section10_body = ""
    section10_body = (
        f"- Version: {(approval_metadata or {}).get('version') or 'draft'}\n"
        f"- Date: {(approval_metadata or {}).get('date') or 'generated'}\n"
        f"- Change summary: Benefit-risk report regenerated from current project evidence.\n"
    )

    decision_owner_line = (
        "Recorded in the controlled document system at approval (name/role per organization procedure)."
        if approved_mode
        else "To be assigned at formal approval."
    )
    decision_date_line = "As recorded on the approved controlled copy." if approved_mode else "To be assigned."

    summary_interp, summary_scope = _scope_empty_interpretation(context)
    summary_extra_lines = ""
    if total == 0:
        summary_extra_lines = f"- Interpretation: {summary_interp}\n- {summary_scope}\n"

    decision_output = decision_text or decision
    rationale_output = rationale_text or (
        "The determination is based on the residual-risk evidence set, linked clinical evidence status, and traceability completeness."
    )
    approval_meta = approval_metadata or {}
    author = approval_meta.get("author") or "Risk Management Author"
    reviewer = approval_meta.get("reviewer") or "Quality/Clinical Reviewer"
    approver = approval_meta.get("approver") or "Approver"
    approval_date = approval_meta.get("date") or "Date not assigned"
    approval_version = approval_meta.get("version") or "Draft"
    issuance_state = approval_meta.get("issuance_state") or ("Approved" if approved_mode else "Draft")

    exec_summary = (
        "The overall benefit-risk profile is acceptable for the intended use based on the evaluated residual-risk evidence."
        if decision_output.lower().startswith("acceptable")
        else "The overall benefit-risk profile cannot be concluded as acceptable until identified blockers are resolved."
    )

    comparison_stmt = (
        "Clinical benefits are assessed against identified residual risks using severity, probability, and acceptability outcomes."
    )
    soa_stmt = (
        "Current state-of-the-art considerations are derived from linked clinical and risk documentation for this project."
    )
    uncertainty_stmt = (
        "Uncertainty is primarily driven by evidence completeness, unresolved risk records, and linkage status of controlled source documents."
    )
    pms_stmt = (
        "Post-market surveillance and reassessment are required to confirm the ongoing validity of this benefit-risk profile."
    )

    return f"""# Benefit-Risk Analysis

## Executive Summary
{exec_summary}

{_project_evidence_banner(context, approved_mode=approved_mode)}

## Document Information
- Project name: {context.get("project_name")}
- Project ID: {context.get("project_id")}
- Device description: {profile.get("device_description") or "Not provided"}
- Intended use: {profile.get("intended_use") or "Not provided"}
- Target population: {profile.get("user_population") or "Not provided"}
- Use environment: {profile.get("use_environment") or "Not provided"}

{_build_report_scope_section(context, approved_mode=approved_mode)}

## Summary of Residual Risks
- Residual severity missing: {missing.get("residual_severity", 0)}
- Residual probability missing: {missing.get("residual_probability", 0)}
- Residual acceptability missing/inferred: {missing.get("acceptability_decision", 0)}
- Linked controls missing: {missing.get("linked_controls", 0)}
- Data quality status: {dqs}
{("- " + dq_extra) if dq_extra else ""}
- Total residual risks screened: {screened}
- Number above threshold (residual score ≥ 20): {above_threshold}
- Number requiring explicit benefit–risk justification (needs_benefit_risk + unacceptable): {requiring_explicit}
- Reported benefit-risk required count: {summary.get("benefit_risk_required_count") or 0}
- Screening rule: residual risk score ≥ 20 and/or acceptability classified as needs benefit-risk review or unacceptable.

- Total residual risks: {total}
{summary_extra_lines}- Acceptable: {acceptable}
- Acceptable with justification: {acceptable_with_just}
- Needs benefit–risk review: {needs_br}
- Unacceptable: {unacceptable}
- Unknown acceptability: {unknown}
- Highest residual severity: {highest_sev if highest_sev is not None else "N/A (no scored rows)"}
- Highest residual risk score: {highest_risk if highest_risk is not None else "N/A (no scored rows)"}

{top_risks_section}

### Control effectiveness summary
- Risks with linked controls: {controls_linked}
- Risks without linked controls: {controls_missing}
- Paired initial/residual comparisons: {rr.get("pairedCount") if rr else 0}
- Reduced after controls: {rr.get("reducedCount") if rr else 0}
- Unchanged after controls: {rr.get("unchangedCount") if rr else 0}
- Worsened after controls: {rr.get("worsenedCount") if rr else 0}

## Elevated Residual Risks Requiring Justification
| Risk ID | Hazard | Harm | Residual Risk | Justification Summary |
|---|---|---|---|---|
{chr(10).join([f"| {r.get('risk_key') or 'N/A'} | {(r.get('hazard') or 'N/A')[:120]} | {(r.get('harm') or 'N/A')[:120]} | {(str(r.get('residual_risk_level') or 'N/A') + ' / ' + str(r.get('residual_risk_score') or 'N/A'))} | Pending formal benefit-risk justification with linked evidence. |" for r in elevated[:10]]) if elevated else "| None in scope | - | - | - | No in-scope residual risks were available for classification as needs_benefit_risk or unacceptable. |"}

## Anticipated Clinical Benefits
- Intended therapeutic benefit: {profile.get("clinical_benefit") or "Missing source: project profile clinical benefit"}
- Primary clinical objective: {profile.get("intended_use") or "Missing source: intended use"}
- Target population benefit: {profile.get("user_population") or "Missing source: user population"}
- Expected outcomes: {profile.get("clinical_benefit") or "Missing source: CER or project clinical evidence"}

## Benefit-Risk Comparison
{comparison_stmt}

## State of the Art Considerations
{soa_stmt}

## Uncertainty and Data Gaps
{uncertainty_stmt}

## Post-Market Surveillance and Reassessment
{pms_stmt}

## Overall Benefit-Risk Decision
- Decision: {decision_output}
- Basis of decision:
  - Residual-risk evidence: {total} row(s) in scope; data quality **{dqs}**; canonical conclusion **{display_final}**{"" if approved_mode else f" (source determination: {raw_final or 'N/A'})"}.
  - Clinical evidence: clinical evaluation document **{'approved' if linked_cer_ok else 'missing or not approved'}** (id={cer_doc.get("id") or "none"}).
  - Traceability completeness: fully traceable {trace.get("fullyTraceable", 0)}; partial {trace.get("partiallyTraceable", 0)}; missing control linkage {trace.get("missingControlLinkage", 0)}; missing verification linkage {trace.get("missingVerificationLinkage", 0)}.
  - Linked source documents: residual risk evaluation **{'approved' if linked_rr_ok else 'missing or not approved'}** (id={rr_doc.get("id") or "none"}).
- Decision confidence: **{confidence}**
- Rationale: {rationale_output}
- Conditions: Resolve all blockers before controlled issuance.
- Decision owner: {decision_owner_line}
- Decision owner role: Risk management lead
- Decision date: {decision_date_line}

## Traceability
{trace_section}
**Traceability summary:** fully traceable {trace.get("fullyTraceable", 0)}; partially traceable {trace.get("partiallyTraceable", 0)}; missing control linkage {trace.get("missingControlLinkage", 0)}; missing verification linkage {trace.get("missingVerificationLinkage", 0)}.

## Approval
- Author: {author}
- Reviewer: {reviewer}
- Approver: {approver}
- Date: {approval_date}
- Version: {approval_version}
- Approval/issuance state: {issuance_state}
{"- Readiness result: BLOCKED\\n- Blockers:\\n" + chr(10).join([f"  - {b}" for b in approved_blockers]) if approved_blockers else "- Readiness result: Ready for issuance."}

{section10_title}
{section10_body}
"""


def _context_to_prompt(context: Dict[str, Any]) -> str:
    """Internal context pack for optional AI helper (not appended to formal report)."""
    profile = context.get("profile") or {}
    summary = context.get("residual_summary") or {}
    top_risks = context.get("top_residual_risks") or []
    snippets = context.get("linked_doc_snippets") or {}

    risk_lines = []
    for r in top_risks:
        risk_lines.append(
            "- risk_key={risk_key} | hazard={hazard} | harm={harm} | "
            "residual_level={residual_risk_level} | residual_score={residual_risk_score} | acceptability={acceptability}".format(
                **r
            )
        )

    return (
        f"Project ID: {context.get('project_id')}\n"
        f"Project name: {context.get('project_name')}\n"
        "Project profile:\n"
        f"- device_description: {profile.get('device_description')}\n"
        f"- intended_use: {profile.get('intended_use')}\n"
        f"- user_population: {profile.get('user_population')}\n"
        f"- use_environment: {profile.get('use_environment')}\n"
        f"- clinical_benefit: {profile.get('clinical_benefit')}\n\n"
        "Residual risk summary:\n"
        f"- final_determination: {summary.get('final_determination')}\n"
        f"- data_quality_status: {summary.get('data_quality_status')}\n"
        f"- total_risk_items: {summary.get('total_risk_items')}\n\n"
        "Top residual risks:\n"
        f"{chr(10).join(risk_lines) if risk_lines else '- none'}\n\n"
        "Linked document excerpts:\n"
        f"- rmp_excerpt: {snippets.get('rmp')}\n"
        f"- hazard_analysis_excerpt: {snippets.get('hazard_analysis')}\n"
        f"- residual_risk_excerpt: {snippets.get('residual_risk')}\n"
        f"- risk_controls_doc_excerpt: {snippets.get('risk_controls_doc')}\n"
    )


def generate_benefit_risk_analysis_draft(
    db: Session,
    *,
    project_id: str,
    project_name: str,
    version_scope: str = "approved_only",
    use_ai: bool = False,
    approved_mode: bool = False,
    decision_text: Optional[str] = None,
    rationale_text: Optional[str] = None,
    approval_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a single coherent benefit–risk report from project evidence.

    - Formal output is always the structured markdown only (no AI addendum in draft_markdown).
    - Optional AI helper text is returned separately as ai_helper_markdown for editor-side use only.
    - approved_mode: stricter validation; raises BenefitRiskApprovedModeBlocked if not issuable.
    """
    context = _build_project_context(
        db,
        project_id=project_id,
        project_name=project_name,
        version_scope=version_scope,
    )

    if approved_mode:
        blockers = _approved_mode_blockers(
            context,
            decision_text=decision_text,
            rationale_text=rationale_text,
            approval_metadata=approval_metadata,
        )
        if blockers:
            raise BenefitRiskApprovedModeBlocked(blockers)

    deterministic_report = _build_decision_grade_report(
        context,
        approved_mode=approved_mode,
        decision_text=decision_text,
        rationale_text=rationale_text,
        approval_metadata=approval_metadata,
    )

    ai_helper: Optional[str] = None
    if use_ai and not approved_mode:
        try:
            from services.project_ai_doc_generator import _default_ai_draft_fn

            prompt_context = _context_to_prompt(context)
            ai_helper = _default_ai_draft_fn(
                "benefit_risk_analysis",
                prompt_context,
                {
                    "project_id": project_id,
                    "project_name": project_name,
                    "doc_type": "benefit_risk_analysis",
                    "mode": "internal_editor_helper_only",
                },
            )
        except Exception:
            ai_helper = None

    return {
        "draft_markdown": deterministic_report,
        "ai_helper_markdown": ai_helper,
        "project_context": context,
    }
