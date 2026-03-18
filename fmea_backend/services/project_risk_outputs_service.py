"""
Phase 4: Generate structured risk outputs from project_risk_items.

Builds FMEA table, Hazard Analysis, Risk Analysis, Risk Control Traceability,
Verification Traceability, Residual Risk Evaluation, and draft RMR sections
from linked project_risk_items, project_risk_controls, project_verifications,
and library/architecture data.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from models.device import Device
from models.project_risk_item import ProjectRiskItem
from models.project_risk_control import ProjectRiskControl
from models.project_verification import ProjectVerification


def _get_project_risk_items_with_relations(
    db: Session, project_id: str, device_id: Optional[str] = None
) -> List[ProjectRiskItem]:
    """Load project risk items for a project (via device.project_id), optionally filtered by device_id."""
    q = (
        db.query(ProjectRiskItem)
        .join(Device, ProjectRiskItem.device_id == Device.id)
        .filter(Device.project_id == project_id)
        .options(
            joinedload(ProjectRiskItem.device),
            joinedload(ProjectRiskItem.component),
            joinedload(ProjectRiskItem.hazard_library),
            joinedload(ProjectRiskItem.harm_library),
            joinedload(ProjectRiskItem.controls)
            .joinedload(ProjectRiskControl.risk_control_library),
            joinedload(ProjectRiskItem.controls)
            .joinedload(ProjectRiskControl.verifications)
            .joinedload(ProjectVerification.verification_library),
        )
        .order_by(ProjectRiskItem.created_at)
    )
    if device_id is not None:
        q = q.filter(ProjectRiskItem.device_id == device_id)
    return q.all()


def _hazard_text(pri: ProjectRiskItem) -> str:
    lib_name = getattr(pri.hazard_library, "hazard_name", None) if pri.hazard_library else None
    return (pri.hazard_text or lib_name or "").strip()


def _harm_text(pri: ProjectRiskItem) -> str:
    lib_name = getattr(pri.harm_library, "harm_name", None) if pri.harm_library else None
    return (pri.harm_text or lib_name or "").strip()


def _control_display(ctrl: ProjectRiskControl) -> str:
    lib_name = getattr(ctrl.risk_control_library, "control_name", None) if ctrl.risk_control_library else None
    return (ctrl.control_text or lib_name or "").strip()


def _verification_display(v: ProjectVerification) -> str:
    lib_name = getattr(v.verification_library, "verification_method", None) if v.verification_library else None
    return (v.verification_text or lib_name or "").strip()


def _verifications_for_risk_item(pri: ProjectRiskItem) -> str:
    """All verification text for a risk item (from all its controls' verifications)."""
    parts = []
    for ctrl in pri.controls:
        for v in (ctrl.verifications or []):
            part = _verification_display(v)
            if part:
                parts.append(part)
    return "\n".join(parts) if parts else ""


def build_fmea_table(
    db: Session, project_id: str, device_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """FMEA table with columns: Component, Failure Mode, Effect, Cause, Severity, Probability,
    Detectability, Risk Score, Risk Control, Verification, Residual Risk. Optional device_id filters to one device."""
    items = _get_project_risk_items_with_relations(db, project_id, device_id)
    rows = []
    for i, pri in enumerate(items):
        component_name = (pri.component.name if pri.component else "") or ""
        controls_list = [_control_display(c) for c in pri.controls]
        risk_control = "\n".join(controls_list) if controls_list else ""
        verification = _verifications_for_risk_item(pri)
        # Residual risk: short summary (e.g. "S/P/D: 1/2/3 — 6 — Acceptable")
        res_s = pri.residual_severity
        res_p = pri.residual_probability
        res_d = pri.residual_detectability
        res_score = pri.residual_risk_score
        res_accept = (pri.residual_risk_acceptability or "").strip()
        if res_s is not None and res_p is not None and res_d is not None:
            residual_risk = f"S/P/D: {res_s}/{res_p}/{res_d}"
            if res_score is not None:
                residual_risk += f" — {res_score}"
            if res_accept:
                residual_risk += f" — {res_accept}"
        elif res_score is not None:
            residual_risk = str(res_score) + (f" — {res_accept}" if res_accept else "")
        else:
            residual_risk = res_accept or ""
        rows.append({
            "id": pri.id,
            "row_number": i + 1,
            "component": component_name,
            "failure_mode": (pri.failure_mode or "").strip(),
            "effect": _harm_text(pri),
            "cause": (pri.hazardous_situation or "").strip() or _hazard_text(pri),
            "severity": pri.severity,
            "probability": pri.probability,
            "detectability": pri.detectability,
            "risk_score": pri.risk_score,
            "risk_control": risk_control,
            "verification": verification,
            "residual_risk": residual_risk,
        })
    return rows


def build_hazard_analysis_table(
    db: Session, project_id: str, device_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Hazard analysis table: Hazard, Hazardous Situation, Harm, Sequence of Events, Severity, Probability."""
    items = _get_project_risk_items_with_relations(db, project_id, device_id)
    rows = []
    for i, pri in enumerate(items):
        # sequence_of_events not on ProjectRiskItem; expose as empty until model has it
        sequence_of_events = getattr(pri, "sequence_of_events", None) or ""
        if isinstance(sequence_of_events, str):
            sequence_of_events = sequence_of_events.strip()
        else:
            sequence_of_events = ""
        rows.append({
            "id": pri.id,
            "row_number": i + 1,
            "hazard": _hazard_text(pri),
            "hazardous_situation": (pri.hazardous_situation or "").strip(),
            "harm": _harm_text(pri),
            "sequence_of_events": sequence_of_events,
            "severity": pri.severity,
            "probability": pri.probability,
        })
    return rows


def build_risk_analysis_table(db: Session, project_id: str) -> List[Dict[str, Any]]:
    """Risk analysis table: risk item ref, hazard, harm, severity, probability, detectability, risk score, acceptability."""
    items = _get_project_risk_items_with_relations(db, project_id)
    rows = []
    for i, pri in enumerate(items):
        controls_list = [_control_display(c) for c in pri.controls]
        rows.append({
            "id": pri.id,
            "row_number": i + 1,
            "device": (pri.device.name if pri.device else "") or "",
            "component": (pri.component.name if pri.component else "") or "",
            "failure_mode": (pri.failure_mode or "").strip(),
            "hazard": _hazard_text(pri),
            "harm": _harm_text(pri),
            "severity": pri.severity,
            "probability": pri.probability,
            "detectability": pri.detectability,
            "risk_score": pri.risk_score,
            "risk_acceptability": pri.risk_acceptability or "",
            "risk_controls_summary": "\n".join(controls_list) if controls_list else "",
            "status": pri.status or "",
        })
    return rows


def _risk_item_label(pri: ProjectRiskItem) -> str:
    """Short label for a risk item (Risk Item column)."""
    comp = (pri.component.name if pri.component else "") or ""
    fm = (pri.failure_mode or "").strip()
    if comp and fm:
        return f"{comp} — {fm}"
    return comp or fm or str(pri.id)[:8]


def build_risk_control_traceability_table(
    db: Session, project_id: str, device_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Risk control traceability: Risk Item, Hazard, Control, Implementation Reference, Verification, Evidence Reference.
    One row per (risk item, control, verification); controls with no verifications get one row with empty verification/evidence."""
    items = _get_project_risk_items_with_relations(db, project_id, device_id)
    rows = []
    for pri in items:
        risk_item = _risk_item_label(pri)
        hazard = _hazard_text(pri)
        for ctrl in pri.controls:
            control_text = _control_display(ctrl)
            impl_ref = (ctrl.implementation_reference or "").strip()
            verifications = list(ctrl.verifications or [])
            if not verifications:
                rows.append({
                    "project_risk_item_id": pri.id,
                    "project_risk_control_id": ctrl.id,
                    "risk_item": risk_item,
                    "hazard": hazard,
                    "control": control_text,
                    "implementation_reference": impl_ref,
                    "verification": "",
                    "evidence_reference": "",
                })
            else:
                for ver in verifications:
                    rows.append({
                        "project_risk_item_id": pri.id,
                        "project_risk_control_id": ctrl.id,
                        "risk_item": risk_item,
                        "hazard": hazard,
                        "control": control_text,
                        "implementation_reference": impl_ref,
                        "verification": _verification_display(ver),
                        "evidence_reference": (ver.evidence_reference or "").strip(),
                    })
    return rows


def build_verification_traceability_table(db: Session, project_id: str) -> List[Dict[str, Any]]:
    """Verification traceability: control → verification method → evidence, status."""
    items = _get_project_risk_items_with_relations(db, project_id)
    rows = []
    for pri in items:
        component_name = (pri.component.name if pri.component else "") or ""
        for ctrl in pri.controls:
            control_display = _control_display(ctrl)
            for ver in ctrl.verifications:
                rows.append({
                    "project_risk_control_id": ctrl.id,
                    "project_verification_id": ver.id,
                    "component": component_name,
                    "control_text": control_display,
                    "verification_text": _verification_display(ver),
                    "verification_library_id": ver.verification_library_id,
                    "evidence_reference": (ver.evidence_reference or "").strip(),
                    "status": ver.status or "pending",
                })
    return rows


def build_residual_risk_evaluation_table(
    db: Session, project_id: str, device_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Residual risk evaluation: Risk Item, Initial Risk, Controls Applied, Residual Severity,
    Residual Probability, Residual Risk Score, Acceptable?"""
    items = _get_project_risk_items_with_relations(db, project_id, device_id)
    rows = []
    for i, pri in enumerate(items):
        # Initial risk: S/P/D and score
        s, p, d = pri.severity, pri.probability, pri.detectability
        if s is not None and p is not None and d is not None:
            initial_risk = f"S/P/D: {s}/{p}/{d}"
            if pri.risk_score is not None:
                initial_risk += f" — {pri.risk_score}"
        else:
            initial_risk = str(pri.risk_score) if pri.risk_score is not None else ""
        controls_applied = "\n".join([_control_display(c) for c in pri.controls]) if pri.controls else ""
        acc = (pri.residual_risk_acceptability or "").strip().lower()
        acceptable = "Yes" if acc in ("acceptable", "yes", "1") else ("No" if acc in ("not acceptable", "unacceptable", "no", "0") else (pri.residual_risk_acceptability or ""))
        rows.append({
            "id": pri.id,
            "row_number": i + 1,
            "risk_item": _risk_item_label(pri),
            "initial_risk": initial_risk,
            "controls_applied": controls_applied,
            "residual_severity": pri.residual_severity,
            "residual_probability": pri.residual_probability,
            "residual_risk_score": pri.residual_risk_score,
            "acceptable": acceptable,
        })
    return rows


def _build_device_report_draft_sections(
    items: List[ProjectRiskItem], device: Optional[Device]
) -> Dict[str, str]:
    """Generate structured draft report section text from accepted project risk items and linked evidence.
    Returns dict of section_key -> narrative text for:
    device_description, hazard_identification, hazardous_situations, potential_harms,
    risk_estimation, risk_evaluation, risk_control_identification, verification_of_risk_controls,
    residual_risk_evaluation, overall_residual_risk_acceptability."""
    device_name = (device.name if device else "").strip() or "Device"
    device_desc = (device.description if device else "").strip() or ""

    # 1. Device Description Relevant to Hazard Analysis
    components = []
    for pri in items:
        comp = (pri.component.name if pri.component else "").strip()
        if comp and comp not in components:
            components.append(comp)
    device_description = (
        f"{device_name}. "
        + (f"{device_desc} " if device_desc else "")
        + (
            f"Components relevant to hazard analysis: {', '.join(components)}."
            if components
            else "No components linked to risk items yet."
        )
    )

    # 2. Hazard Identification
    hazards_seen = []
    hazard_lines = []
    for pri in items:
        h = _hazard_text(pri)
        if h and h not in hazards_seen:
            hazards_seen.append(h)
            hazard_lines.append(f"- {h}")
    hazard_identification = (
        "\n".join(hazard_lines) if hazard_lines else "No hazards identified for this device in accepted risk items."
    )

    # 3. Hazardous Situations
    sit_seen = []
    sit_lines = []
    for pri in items:
        s = (pri.hazardous_situation or "").strip()
        if s and s not in sit_seen:
            sit_seen.append(s)
            hazard_label = _hazard_text(pri) or "—"
            sit_lines.append(f"- **{hazard_label}**: {s}")
    hazardous_situations = (
        "\n".join(sit_lines) if sit_lines else "No hazardous situations recorded."
    )

    # 4. Potential Harms
    harm_seen = []
    harm_lines = []
    for pri in items:
        harm = _harm_text(pri)
        if harm and harm not in harm_seen:
            harm_seen.append(harm)
            harm_lines.append(f"- {harm}")
    potential_harms = (
        "\n".join(harm_lines) if harm_lines else "No potential harms recorded."
    )

    # 5. Risk Estimation (S, P, D, risk score per item)
    est_lines = []
    for pri in items:
        comp = (pri.component.name if pri.component else "").strip() or "—"
        fm = (pri.failure_mode or "").strip() or "—"
        h = _hazard_text(pri) or "—"
        s, p, d = pri.severity, pri.probability, pri.detectability
        score = pri.risk_score
        est_lines.append(
            f"- **{comp}** / {fm} | Hazard: {h} — Severity: {s or '—'}, Probability: {p or '—'}, Detectability: {d or '—'}; Risk score: {score or '—'}"
        )
    risk_estimation = (
        "\n".join(est_lines) if est_lines else "No risk estimation data (S, P, D) for this device."
    )

    # 6. Risk Evaluation (acceptability)
    eval_lines = []
    for pri in items:
        comp = (pri.component.name if pri.component else "").strip() or "—"
        acc = (pri.risk_acceptability or "").strip() or "—"
        score = pri.risk_score
        eval_lines.append(f"- **{comp}**: Inherent risk score {score or '—'}; acceptability: {acc}")
    risk_evaluation = (
        "\n".join(eval_lines) if eval_lines else "No risk evaluation (acceptability) recorded."
    )

    # 7. Risk Control Identification
    ctrl_lines = []
    for pri in items:
        comp = (pri.component.name if pri.component else "").strip() or "—"
        h = _hazard_text(pri) or "—"
        for c in pri.controls:
            ctrl_lines.append(f"- **{comp}** / {h}: {_control_display(c)}")
    risk_control_identification = (
        "\n".join(ctrl_lines) if ctrl_lines else "No risk controls identified for this device."
    )

    # 8. Verification of Risk Controls
    ver_lines = []
    for pri in items:
        for c in pri.controls:
            ctrl_text = _control_display(c)
            for v in (c.verifications or []):
                ver_text = _verification_display(v)
                ev_ref = (v.evidence_reference or "").strip()
                ver_lines.append(
                    f"- Control: {ctrl_text} — Verification: {ver_text}"
                    + (f" (Evidence: {ev_ref})" if ev_ref else "")
                )
    verification_of_risk_controls = (
        "\n".join(ver_lines) if ver_lines else "No verification of risk controls recorded."
    )

    # 9. Residual Risk Evaluation
    res_lines = []
    for pri in items:
        comp = (pri.component.name if pri.component else "").strip() or "—"
        rs, rp, rd = pri.residual_severity, pri.residual_probability, pri.residual_detectability
        rscore = pri.residual_risk_score
        acc = (pri.residual_risk_acceptability or "").strip() or "—"
        res_lines.append(
            f"- **{comp}**: Residual S={rs or '—'}, P={rp or '—'}, D={rd or '—'}; score: {rscore or '—'}; acceptability: {acc}"
        )
    residual_risk_evaluation = (
        "\n".join(res_lines) if res_lines else "No residual risk evaluation for this device."
    )

    # 10. Overall Residual Risk Acceptability
    acceptable_count = sum(
        1 for pri in items
        if (pri.residual_risk_acceptability or "").strip().lower() in ("acceptable", "yes", "1")
    )
    not_acceptable_count = sum(
        1 for pri in items
        if (pri.residual_risk_acceptability or "").strip().lower() in ("not acceptable", "unacceptable", "no", "0")
    )
    other_count = len(items) - acceptable_count - not_acceptable_count
    parts = []
    if acceptable_count:
        parts.append(f"{acceptable_count} risk item(s) with residual risk acceptable.")
    if not_acceptable_count:
        parts.append(f"{not_acceptable_count} risk item(s) with residual risk not acceptable.")
    if other_count:
        parts.append(f"{other_count} risk item(s) with residual risk acceptability not classified.")
    overall_residual_risk_acceptability = (
        " ".join(parts) if parts else "No residual risk acceptability data for this device."
    )

    return {
        "device_description": device_description,
        "hazard_identification": hazard_identification,
        "hazardous_situations": hazardous_situations,
        "potential_harms": potential_harms,
        "risk_estimation": risk_estimation,
        "risk_evaluation": risk_evaluation,
        "risk_control_identification": risk_control_identification,
        "verification_of_risk_controls": verification_of_risk_controls,
        "residual_risk_evaluation": residual_risk_evaluation,
        "overall_residual_risk_acceptability": overall_residual_risk_acceptability,
    }


def build_device_report_content(
    db: Session, project_id: str, device_id: str
) -> Dict[str, Any]:
    """Build device-scoped report content (markdown and JSON) for generate-report.
    Includes structured draft sections plus FMEA/hazard/traceability/residual tables.
    Returns dict with content_markdown, content_json."""
    items = _get_project_risk_items_with_relations(db, project_id, device_id)
    device = db.query(Device).filter(Device.id == device_id).first()
    draft_sections = _build_device_report_draft_sections(items, device)

    fmea_rows = build_fmea_table(db, project_id, device_id)
    hazard_rows = build_hazard_analysis_table(db, project_id, device_id)
    trace_rows = build_risk_control_traceability_table(db, project_id, device_id)
    residual_rows = build_residual_risk_evaluation_table(db, project_id, device_id)

    # Structured draft sections (narrative) first in markdown
    section_titles = [
        ("device_description", "Device Description Relevant to Hazard Analysis"),
        ("hazard_identification", "Hazard Identification"),
        ("hazardous_situations", "Hazardous Situations"),
        ("potential_harms", "Potential Harms"),
        ("risk_estimation", "Risk Estimation"),
        ("risk_evaluation", "Risk Evaluation"),
        ("risk_control_identification", "Risk Control Identification"),
        ("verification_of_risk_controls", "Verification of Risk Controls"),
        ("residual_risk_evaluation", "Residual Risk Evaluation"),
        ("overall_residual_risk_acceptability", "Overall Residual Risk Acceptability"),
    ]
    sections = []
    for key, title in section_titles:
        text = draft_sections.get(key, "")
        sections.append(f"## {title}\n\n{text}\n\n")

    # Then data tables
    sections.append("## FMEA\n")
    if fmea_rows:
        sections.append("| Component | Failure Mode | Effect | Cause | S | P | D | Risk Score | Risk Control | Verification | Residual Risk |")
        sections.append("|-----------|--------------|--------|-------|---|---|---|------------|--------------|--------------|---------------|")
        for r in fmea_rows:
            row = "|".join([
                str((r.get("component") or ""))[:30],
                str((r.get("failure_mode") or ""))[:30],
                str((r.get("effect") or ""))[:20],
                str((r.get("cause") or ""))[:20],
                str(r.get("severity") or ""),
                str(r.get("probability") or ""),
                str(r.get("detectability") or ""),
                str(r.get("risk_score") or ""),
                str((r.get("risk_control") or ""))[:25],
                str((r.get("verification") or ""))[:25],
                str((r.get("residual_risk") or ""))[:20],
            ])
            sections.append("|" + row + "|")
    else:
        sections.append("No FMEA data for this device.")
    sections.append("\n## Hazard Analysis\n")
    if hazard_rows:
        sections.append("| Hazard | Hazardous Situation | Harm | Sequence of Events | Severity | Probability |")
        sections.append("|--------|---------------------|------|--------------------|----------|-------------|")
        for r in hazard_rows:
            row = "|".join([
                str((r.get("hazard") or ""))[:25],
                str((r.get("hazardous_situation") or ""))[:25],
                str((r.get("harm") or ""))[:20],
                str((r.get("sequence_of_events") or ""))[:20],
                str(r.get("severity") or ""),
                str(r.get("probability") or ""),
            ])
            sections.append("|" + row + "|")
    else:
        sections.append("No hazard analysis data for this device.")
    sections.append("\n## Risk Control Traceability\n")
    if trace_rows:
        sections.append("| Risk Item | Hazard | Control | Implementation Reference | Verification | Evidence Reference |")
        sections.append("|-----------|--------|---------|--------------------------|--------------|---------------------|")
        for r in trace_rows:
            row = "|".join([
                str((r.get("risk_item") or ""))[:20],
                str((r.get("hazard") or ""))[:20],
                str((r.get("control") or ""))[:25],
                str((r.get("implementation_reference") or ""))[:25],
                str((r.get("verification") or ""))[:20],
                str((r.get("evidence_reference") or ""))[:20],
            ])
            sections.append("|" + row + "|")
    else:
        sections.append("No risk control traceability for this device.")
    sections.append("\n## Residual Risk Evaluation\n")
    if residual_rows:
        sections.append("| Risk Item | Initial Risk | Controls Applied | Residual Severity | Residual Probability | Residual Risk Score | Acceptable? |")
        sections.append("|-----------|--------------|------------------|-------------------|---------------------|--------------------|-------------|")
        for r in residual_rows:
            row = "|".join([
                str((r.get("risk_item") or ""))[:20],
                str((r.get("initial_risk") or ""))[:15],
                str((r.get("controls_applied") or ""))[:25],
                str(r.get("residual_severity") or ""),
                str(r.get("residual_probability") or ""),
                str(r.get("residual_risk_score") or ""),
                str((r.get("acceptable") or "")),
            ])
            sections.append("|" + row + "|")
    else:
        sections.append("No residual risk data for this device.")

    content_markdown = "\n".join(sections)
    content_json = {
        "report_sections": draft_sections,
        "fmea": fmea_rows,
        "hazard_analysis": hazard_rows,
        "risk_traceability": trace_rows,
        "residual_risk": residual_rows,
    }
    return {"content_markdown": content_markdown, "content_json": content_json}


def build_risk_management_report_draft(db: Session, project_id: str) -> Dict[str, Any]:
    """Draft Risk Management Report sections generated from structured project risk data."""
    items = _get_project_risk_items_with_relations(db, project_id)
    fmea_rows = build_fmea_table(db, project_id)
    hazard_rows = build_hazard_analysis_table(db, project_id)
    residual_rows = build_residual_risk_evaluation_table(db, project_id)

    def _section(title: str, content: str) -> str:
        return f"## {title}\n\n{content}\n\n"

    # 1. Scope / Introduction (placeholder + data summary)
    intro = (
        "This draft Risk Management Report is generated from project risk items (accepted suggestions and linked library data). "
        "It provides traceability from components through failure modes, hazards, harms, risk controls, and verification.\n\n"
        f"**Summary:** {len(items)} risk item(s); {len(hazard_rows)} hazard analysis row(s); {len(residual_rows)} residual risk evaluation row(s).\n\n"
    )

    # 2. Hazard analysis summary
    hazard_lines = []
    for r in hazard_rows:
        hazard_lines.append(
            f"- **{r.get('hazard', '') or '(Hazard)'}** — Hazardous situation: {r.get('hazardous_situation', '') or '—'}; "
            f"Harm: {r.get('harm', '') or '—'}; S={r.get('severity') or '—'}, P={r.get('probability') or '—'}."
        )
    hazard_section = "\n".join(hazard_lines) if hazard_lines else "No hazard analysis data yet. Accept component suggestions to populate."

    # 3. Risk analysis summary (FMEA columns: component, failure_mode, effect, cause, S, P, D, risk_score, risk_control, verification, residual_risk)
    risk_lines = []
    for r in fmea_rows:
        risk_lines.append(
            f"- Component: {r.get('component', '')}; Failure mode: {r.get('failure_mode', '') or '—'}; "
            f"Effect: {r.get('effect', '') or '—'}; Cause: {r.get('cause', '') or '—'}; "
            f"S={r.get('severity') or '—'}, P={r.get('probability') or '—'}, D={r.get('detectability') or '—'}; "
            f"Risk score: {r.get('risk_score') or '—'}; Residual risk: {r.get('residual_risk', '') or '—'}."
        )
    risk_section = "\n".join(risk_lines) if risk_lines else "No risk analysis data yet."

    # 4. Risk controls summary
    control_lines = []
    for pri in items:
        comp = (pri.component.name if pri.component else "") or ""
        hazard = _hazard_text(pri)
        for c in pri.controls:
            control_lines.append(f"- **{comp}** / {hazard}: {_control_display(c)}")
    controls_section = "\n".join(control_lines) if control_lines else "No risk controls recorded yet."

    # 5. Verification summary
    ver_lines = []
    for pri in items:
        for c in pri.controls:
            for v in c.verifications:
                ver_lines.append(f"- Control: {_control_display(c)} → Verification: {_verification_display(v)} (Status: {v.status or 'pending'})")
    verification_section = "\n".join(ver_lines) if ver_lines else "No verification records yet."

    # 6. Residual risk evaluation summary
    residual_lines = []
    for r in residual_rows:
        residual_lines.append(
            f"- **{r.get('risk_item', '') or '—'}** — Initial: {r.get('initial_risk', '') or '—'}; "
            f"Residual S={r.get('residual_severity') or '—'}, P={r.get('residual_probability') or '—'}; "
            f"Score: {r.get('residual_risk_score') or '—'}; Acceptable? {r.get('acceptable', '') or '—'}."
        )
    residual_section = "\n".join(residual_lines) if residual_lines else "No residual risk evaluation data yet."

    # 7. Traceability note
    trace_note = (
        "Traceability is maintained from component → failure mode → hazard → hazardous situation → harm → "
        "risk control → verification. Use the Risk Control Traceability and Verification Traceability tables for full mapping."
    )

    full_draft = (
        _section("1. Introduction / Scope", intro)
        + _section("2. Hazard Analysis Summary", hazard_section)
        + _section("3. Risk Analysis Summary", risk_section)
        + _section("4. Risk Controls Summary", controls_section)
        + _section("5. Verification Summary", verification_section)
        + _section("6. Residual Risk Evaluation Summary", residual_section)
        + _section("7. Traceability", trace_note)
    )

    return {
        "sections": {
            "introduction": intro,
            "hazard_analysis_summary": hazard_section,
            "risk_analysis_summary": risk_section,
            "risk_controls_summary": controls_section,
            "verification_summary": verification_section,
            "residual_risk_summary": residual_section,
            "traceability": trace_note,
        },
        "full_draft": full_draft,
        "stats": {
            "risk_items_count": len(items),
            "hazard_rows_count": len(hazard_rows),
            "fmea_rows_count": len(fmea_rows),
            "residual_rows_count": len(residual_rows),
        },
    }
