from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from business_logic.project_initializer import initialize_project_required_docs
from crud import component as component_crud
from crud import project_profile as profile_crud
from crud import document as document_crud
from crud import fmea as fmea_crud
from models.risk_item import RiskItem
from models.risk_control import RiskControl
from models.document import Document
from models.fmea import FMEARow
from schemas.document import DocumentUpdate
from schemas.fmea import FMEARowCreate


@dataclass
class InitFromProfileStats:
    created_required_docs: int = 0
    updated_documents: List[str] = None  # doc types updated
    seeded_fmea_rows: int = 0

    def __post_init__(self):
        if self.updated_documents is None:
            self.updated_documents = []

    def as_dict(self) -> dict:
        return {
            "created_required_docs": self.created_required_docs,
            "updated_documents": self.updated_documents,
            "seeded_fmea_rows": self.seeded_fmea_rows,
        }


def _is_emptyish(content: Optional[str]) -> bool:
    return not (content or "").strip()


def _status_is_not_started(status: Optional[str]) -> bool:
    if status is None:
        return False
    s = str(status).strip().lower()
    return s in {"not started", "not_started", "not-started"}


def _content_is_placeholder_for_type(doc_type: str, content: Optional[str]) -> bool:
    c = (content or "").strip().lower()
    if not c:
        return True

    # These come from business_logic/project_initializer._default_content_for
    if doc_type == "hazard_analysis" and "hazard analysis export configuration starter" in c:
        return True
    if doc_type == "fmea" and c.startswith("fmea starter"):
        return True
    if doc_type == "design_inputs_doc" and c.startswith("design inputs documentation starter"):
        return True
    if doc_type == "design_dev_plan" and c.startswith("design & development plan starter"):
        return True
    if doc_type == "risk_acceptability_criteria" and c.startswith("risk acceptability criteria starter"):
        return True
    if doc_type == "rmp" and c.startswith("rmp starter"):
        return True
    if doc_type == "design_outputs_doc" and c.startswith("design outputs documentation starter"):
        return True
    if doc_type == "design_reviews" and c.startswith("design reviews starter"):
        return True
    if doc_type == "design_change_record" and c.startswith("design change record starter"):
        return True
    if doc_type == "vv_plan" and c.startswith("v&v plan starter"):
        return True
    if doc_type == "vv_evidence" and c.startswith("v&v evidence report starter"):
        return True
    if doc_type == "validation_summary" and c.startswith("validation summary starter"):
        return True
    if doc_type == "traceability_matrix" and c.startswith("traceability matrix export configuration starter"):
        return True
    if doc_type == "change_impact_analysis" and c.startswith("change impact analysis starter"):
        return True
    if doc_type == "pms_plan" and c.startswith("pms plan starter"):
        return True
    if doc_type == "pms_report" and c.startswith("pms report starter"):
        return True
    if doc_type == "capa" and c.startswith("capa starter"):
        return True
    if doc_type == "usability_risk_analysis" and c.startswith("usability risk analysis starter"):
        return True
    if doc_type == "hf_validation" and c.startswith("human factors validation starter"):
        return True
    if doc_type == "residual_risk" and c.startswith("residual risk evaluation export configuration starter"):
        return True
    if doc_type == "benefit_risk_analysis" and c.startswith("benefit–risk analysis starter"):
        return True
    if doc_type == "risk_controls_doc" and c.startswith("risk control measures documentation export configuration starter"):
        return True
    if doc_type == "risk_management_review" and c.startswith("risk management review starter"):
        return True

    return False


def _draft_design_dev_plan(*, project_id: str, profile: Any, components: list[Any], refs: dict[str, Any]) -> str:
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    def _ref_line(label: str, doc: Any, doc_type: str) -> str:
        if not doc:
            return f"- {label}: (type={doc_type}) — (not present yet)"
        return f"- {label}: doc_id={getattr(doc, 'id', '')} (type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"

    comp_lines = []
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        comp_lines.append(f"- {c.name}{(': ' + c.description) if getattr(c, 'description', None) else ''} (component_id={c.id})")
    if not comp_lines:
        comp_lines = ["- (No components defined yet)"]

    return (
        "Design & Development Plan — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        f"Device description (from profile): {device_desc or 'TBD'}\n"
        f"Intended use (from profile): {intended_use or 'TBD'}\n"
        "\n"
        "Purpose\n"
        "- Defines planned design and development activities, responsibilities, deliverables, and reviews.\n"
        "- This is a conservative template and must be tailored and approved by the team.\n"
        "\n"
        "System Breakdown (from project components)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "Project Phases / Timeline (placeholders)\n"
        "- Concept / Feasibility: (TBD)\n"
        "- Design / Development: (TBD)\n"
        "- Verification: (TBD)\n"
        "- Validation: (TBD)\n"
        "- Transfer / Release: (TBD)\n"
        "\n"
        "Roles and Responsibilities (placeholders)\n"
        "- Project Owner: (TBD)\n"
        "- Engineering Lead: (TBD)\n"
        "- QA/RA: (TBD)\n"
        "- Clinical/Safety: (TBD)\n"
        "- Manufacturing/Operations: (TBD)\n"
        "\n"
        "Deliverables by Phase (placeholders)\n"
        "- Concept: (TBD)\n"
        "- Design: (TBD)\n"
        "- Verification: (TBD)\n"
        "- Validation: (TBD)\n"
        "- Transfer: (TBD)\n"
        "\n"
        "Review Cadence (placeholders)\n"
        "- Design reviews planned: (TBD)\n"
        "- Periodic risk reviews planned: (TBD)\n"
        "\n"
        "References (auto-listed)\n"
        + _ref_line("Design Inputs Documentation", refs.get("design_inputs_doc"), "design_inputs_doc")
        + "\n"
        + _ref_line("Design Outputs Documentation", refs.get("design_outputs_doc"), "design_outputs_doc")
        + "\n"
        + _ref_line("Design Reviews", refs.get("design_reviews"), "design_reviews")
        + "\n"
        + _ref_line("Design Change Record", refs.get("design_change_record"), "design_change_record")
        + "\n"
    )


def _draft_design_reviews(*, project_id: str, profile: Any, refs: dict[str, Any]) -> str:
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    def _fmt(label: str, doc: Any, doc_type: str) -> str:
        if not doc:
            return f"- {label}: (type={doc_type}) — (not present yet)"
        return f"- {label}: doc_id={getattr(doc, 'id', '')} (type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"

    reviewed = [
        _fmt("Design Inputs Documentation", refs.get("design_inputs_doc"), "design_inputs_doc"),
        _fmt("Design Outputs Documentation", refs.get("design_outputs_doc"), "design_outputs_doc"),
        _fmt("Hazard Analysis", refs.get("hazard_analysis"), "hazard_analysis"),
        _fmt("FMEA", refs.get("fmea"), "fmea"),
        _fmt("Risk Control Measures Documentation", refs.get("risk_controls_doc"), "risk_controls_doc"),
        _fmt("V&V Plan", refs.get("vv_plan"), "vv_plan"),
    ]

    return (
        "Design Reviews — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        f"Device description (from profile): {device_desc or 'TBD'}\n"
        f"Intended use (from profile): {intended_use or 'TBD'}\n"
        "\n"
        "Review Record Template (repeat per review)\n"
        "- Review title/type: (e.g., System Requirements Review / Design Review / Verification Readiness) — TBD\n"
        "- Date: (blank — entered by the team)\n"
        "- Attendees: (blank)\n"
        "- Approvals / Sign-off: (blank — do not imply approval)\n"
        "\n"
        "Reviewed Artifacts (auto-listed references)\n"
        + "\n".join(reviewed)
        + "\n\n"
        "Summary of Issues (blank)\n"
        "- \n"
        "\n"
        "Actions / Owners / Due Dates (blank)\n"
        "- Action: ____  Owner: ____  Due: ____\n"
    )


def _draft_design_change_record_base(*, project_id: str, profile: Any) -> str:
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    return (
        "Design Change Record — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        f"Device description (from profile): {device_desc or 'TBD'}\n"
        f"Intended use (from profile): {intended_use or 'TBD'}\n"
        "\n"
        "Purpose\n"
        "- Captures design/document changes and candidate impacted artifacts for subsequent assessment.\n"
        "- SmartQS may append change entries when project documents create new versions.\n"
        "- This record does NOT infer impact conclusions or approvals.\n"
        "\n"
        "Change Entries\n"
        "- (No change entries yet.)\n"
    )


def _build_validation_summary(*, project_id: str, profile: Any, vv_evidence_doc: Any, residual_risk_doc: Any) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""

    vv_ref = (
        f"V&V Evidence Report reference: doc_id={getattr(vv_evidence_doc, 'id', '')} "
        f"(status={getattr(vv_evidence_doc, 'status', '')}, version=v{getattr(vv_evidence_doc, 'version', '')})"
        if vv_evidence_doc is not None
        else "V&V Evidence Report reference: (type=vv_evidence) — (not present yet)"
    )
    rr_ref = (
        f"Residual Risk Evaluation reference: doc_id={getattr(residual_risk_doc, 'id', '')} "
        f"(status={getattr(residual_risk_doc, 'status', '')}, version=v{getattr(residual_risk_doc, 'version', '')})"
        if residual_risk_doc is not None
        else "Residual Risk Evaluation reference: (type=residual_risk) — (not present yet)"
    )

    return (
        "Validation Summary — Draft\n"
        "\n"
        "NOT COMPLETE — Validation Summary cannot be finalized until validation evidence is recorded in the V&V Evidence Report.\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "1. Intended Use Summary (from Project Profile)\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- Device description: {device_desc or 'TBD'}\n"
        f"- User population: {user_pop or 'TBD'}\n"
        f"- Use environment: {use_env or 'TBD'}\n"
        "\n"
        "2. Validation Approach Summary (Draft placeholder)\n"
        "- (TBD — summarize validation strategy, simulated/actual use conditions, and clinical/user needs coverage)\n"
        "\n"
        "3. Summary of Validation Evidence (placeholders)\n"
        f"- {vv_ref}\n"
        "- Evidence summary: (TBD — link/upload evidence and summarize results; do not claim completion here)\n"
        "\n"
        "4. Residual Risks Summary Reference (placeholder)\n"
        f"- {rr_ref}\n"
        "- Residual risks summary: (TBD — reference approved residual risk evaluation)\n"
        "\n"
        "5. Conclusions\n"
        "- Not complete until validation evidence is recorded and reviewed.\n"
        "- (No compliance claims are made in this draft.)\n"
    )


def _draft_pms_plan(
    *,
    project_id: str,
    profile: Any,
    components: list[Any],
    refs: dict[str, Any],
    risks_exist: bool,
) -> str:
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""

    def _ref(label: str, doc: Any, doc_type: str) -> str:
        if not doc:
            return f"- {label}: (type={doc_type}) — (not present yet)"
        return f"- {label}: doc_id={getattr(doc, 'id', '')} (type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"

    comp_lines = []
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        comp_lines.append(f"- {c.name}{(': ' + c.description) if getattr(c, 'description', None) else ''} (component_id={c.id})")
    if not comp_lines:
        comp_lines = ["- (No components defined yet)"]

    risk_note = (
        "- Related risks exist in this project (review Hazard Analysis/FMEA/Risk Controls to focus PMS).\n"
        if risks_exist
        else "- No risk items detected yet. Add hazards/risks to focus PMS over time.\n"
    )

    return (
        "PMS Plan — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT SCAFFOLD (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "Purpose & Scope (Draft)\n"
        "- Defines the planned post-market surveillance (PMS) activities for the device.\n"
        "- Structure-only: does not imply data collection has occurred or that signals exist.\n"
        "\n"
        "Device Overview (from Project Profile)\n"
        f"- Device description: {device_desc or 'TBD'}\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- User population: {user_pop or 'TBD'}\n"
        f"- Use environment: {use_env or 'TBD'}\n"
        "\n"
        "PMS Objectives (placeholders)\n"
        "- (TBD) Monitor safety and performance trends.\n"
        "- (TBD) Detect new hazards/risks and changes in known risks.\n"
        "- (TBD) Feed back into risk management and design controls.\n"
        "\n"
        "Data Sources (structure only)\n"
        "- Complaints\n"
        "- Service / returns / repairs\n"
        "- Literature and registries\n"
        "- Vigilance / regulatory reporting\n"
        "- User feedback (as applicable)\n"
        "- Supplier data (as applicable)\n"
        "\n"
        "Collection Methods & Frequency (placeholders)\n"
        "- Data collection cadence: (TBD)\n"
        "- Review cadence: (TBD)\n"
        "- Data owners/inputs: (TBD)\n"
        "\n"
        "Signal Detection Approach (structure only)\n"
        "- Define signal criteria and triage workflow. (TBD)\n"
        "- Define trend monitoring approach. (TBD)\n"
        "\n"
        "Escalation Criteria (placeholders; do not invent thresholds)\n"
        "- Escalation triggers: (TBD)\n"
        "- Reportability review: (TBD)\n"
        "\n"
        "Roles & Responsibilities (placeholders)\n"
        "- PMS Owner: (TBD)\n"
        "- QA/RA: (TBD)\n"
        "- Clinical/Safety: (TBD)\n"
        "- Engineering: (TBD)\n"
        "\n"
        "Linkage to Risk Management (references only)\n"
        + _ref("Hazard Analysis", refs.get("hazard_analysis"), "hazard_analysis")
        + "\n"
        + _ref("FMEA", refs.get("fmea"), "fmea")
        + "\n"
        + _ref("Risk Controls", refs.get("risk_controls_doc"), "risk_controls_doc")
        + "\n\n"
        "Risk/Component Focus\n"
        + risk_note
        + "\n"
        "Components in scope (from Components list)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "PMS Focus Areas (placeholders; mark areas to monitor)\n"
        "- Component/area: ____  Rationale: ____  Data sources: ____  Frequency: ____\n"
    )


def _draft_pms_report(*, project_id: str, profile: Any, refs: dict[str, Any]) -> str:
    def _ref(label: str, doc: Any, doc_type: str) -> str:
        if not doc:
            return f"- {label}: (type={doc_type}) — (not present yet)"
        return f"- {label}: doc_id={getattr(doc, 'id', '')} (type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"

    return (
        "PMS Report — Draft\n"
        "\n"
        "DRAFT — No PMS data included. Populate after post-market data exists.\n"
        "\n"
        "SYSTEM-GENERATED DRAFT TEMPLATE (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "Reporting Period (blank)\n"
        "- Start date: \n"
        "- End date: \n"
        "- Markets / regions: \n"
        "\n"
        "Summary of Data Reviewed (placeholders)\n"
        "- Complaints reviewed: (TBD)\n"
        "- Service/returns reviewed: (TBD)\n"
        "- Literature/registry review: (TBD)\n"
        "- Vigilance review: (TBD)\n"
        "\n"
        "Signals Identified (empty; populate when signals exist)\n"
        "signal_id | description | source | status | notes\n"
        "-" * 72
        + "\n"
        "\n"
        "Trend Analysis (placeholder)\n"
        "- (TBD)\n"
        "\n"
        "Actions Taken (placeholder)\n"
        "- (TBD)\n"
        "\n"
        "References\n"
        + _ref("PMS Plan", refs.get("pms_plan"), "pms_plan")
        + "\n"
        + _ref("Hazard Analysis", refs.get("hazard_analysis"), "hazard_analysis")
        + "\n"
        + _ref("FMEA", refs.get("fmea"), "fmea")
        + "\n"
    )


def _draft_capa_log(*, project_id: str, profile: Any) -> str:
    return (
        "CAPA — Draft (CAPA Log)\n"
        "\n"
        "SYSTEM-GENERATED DRAFT SCAFFOLD (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "Important\n"
        "- Structure-only: do not record effectiveness confirmation unless objective evidence exists.\n"
        "- Entries below are placeholders; create/track real CAPAs as they occur.\n"
        "\n"
        "CAPA Entries\n"
        "\n"
        "CAPA-001 — Draft (sample empty entry)\n"
        "- Trigger reference: (blank — complaint/quality event/nonconformance reference or free text)\n"
        "- Problem statement: (blank)\n"
        "- Containment: (blank)\n"
        "- Root cause analysis: (blank)\n"
        "- Corrective action(s): (blank)\n"
        "- Preventive action(s): (blank)\n"
        "- Verification of effectiveness plan: (blank)\n"
        "- Status: Open\n"
        "- Owner: (blank)\n"
        "- Dates: Opened ____  Target ____  Closed ____\n"
        "\n"
        "Risk linkage (optional; placeholders)\n"
        "- Related hazard(s): (blank)\n"
        "- Related FMEA row(s): (blank)\n"
        "- Related risk control(s): (blank)\n"
    )


def _draft_usability_risk_analysis(
    *,
    project_id: str,
    profile: Any,
    components: list[Any],
    refs: dict[str, Any],
) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""

    def _ref(label: str, doc: Any, doc_type: str) -> str:
        if not doc:
            return f"- {label}: (type={doc_type}) — (not present yet)"
        return f"- {label}: doc_id={getattr(doc, 'id', '')} (type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"

    ui_elements = []
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        ui_elements.append(f"- {c.name} (use interface element placeholder; component_id={c.id})")
    if not ui_elements:
        ui_elements = ["- (No components defined yet)"]

    return (
        "Usability Risk Analysis — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT SCAFFOLD (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "Purpose & Scope (Draft)\n"
        "- Identify and manage use-related hazards, use errors, foreseeable misuse, and UI/training/labeling dependencies.\n"
        "- Structure-only: does not claim testing or validation has occurred.\n"
        "\n"
        "Use Context Summary (from Project Profile)\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- Device description: {device_desc or 'TBD'}\n"
        f"- Intended users / user population: {user_pop or 'TBD'}\n"
        f"- Use environment: {use_env or 'TBD'}\n"
        "\n"
        "Use Interface Elements (placeholders; derived from Components)\n"
        + "\n".join(ui_elements)
        + "\n\n"
        "User Tasks / Critical Tasks (placeholders)\n"
        "- Task: ____  Critical? (Y/N)  Notes: ____\n"
        "\n"
        "Use-Related Hazard Categories (seeded; deterministic)\n"
        "- Incorrect setup/configuration\n"
        "- Incorrect operation/use steps\n"
        "- Misinterpretation of displays/indicators\n"
        "- Incorrect maintenance/cleaning (if applicable)\n"
        "- Alarm/alert misunderstanding (if applicable)\n"
        "- Foreseeable misuse scenarios\n"
        "\n"
        "Use Error Analysis Table (Draft scaffold; no risk scores)\n"
        "user_task | use_error | potential_harm | contributing_factors | risk_control (UI/training/labeling) | verification_method (TBD) | status\n"
        + ("-" * 120)
        + "\n"
        "\n"
        "Link to Risk Management (references only)\n"
        + _ref("Hazard Analysis", refs.get("hazard_analysis"), "hazard_analysis")
        + "\n"
        + _ref("FMEA", refs.get("fmea"), "fmea")
        + "\n"
        + _ref("Risk Controls", refs.get("risk_controls_doc"), "risk_controls_doc")
        + "\n"
    )


def _draft_hf_validation(
    *,
    project_id: str,
    profile: Any,
) -> str:
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    return (
        "Human Factors Validation — Draft\n"
        "\n"
        "DRAFT — NOT EXECUTED. This document is a scaffold; attach study protocol/results when performed.\n"
        "\n"
        "SYSTEM-GENERATED DRAFT SCAFFOLD (deterministic)\n"
        f"Project ID: {project_id}\n"
        "\n"
        "Purpose & Scope (Draft)\n"
        "- Plan and record human factors validation activities and evidence.\n"
        "- Structure-only: no implied execution, no compliance claims.\n"
        "\n"
        "Intended users and use environments (from Project Profile)\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- Intended users / user population: {user_pop or 'TBD'}\n"
        f"- Use environment(s): {use_env or 'TBD'}\n"
        "\n"
        "Critical Tasks to Validate (placeholders)\n"
        "- Task: ____  Rationale: ____\n"
        "\n"
        "Study Design Overview (placeholders)\n"
        "- Formative vs summative: (TBD)\n"
        "- Sample size: (TBD)\n"
        "- Participant characteristics: (TBD)\n"
        "- Use scenarios: (TBD)\n"
        "\n"
        "Acceptance Criteria (TBD — do not invent thresholds)\n"
        "- (TBD)\n"
        "\n"
        "Deviations Handling (placeholder)\n"
        "- (TBD)\n"
        "\n"
        "Results Summary\n"
        "- Status: Not Executed\n"
        "- (Do not populate until study is performed and evidence is recorded.)\n"
        "\n"
        "Evidence Slots (align these to the Critical Tasks list)\n"
        "task_name | observation/evidence_link | result | notes/deviations\n"
        + ("-" * 96)
        + "\n"
        "- (Add one row per critical task; default Result = Not Executed)\n"
    )


def _draft_risk_acceptability_criteria(*, project_id: str, profile: Any, residual_risk_doc: Any) -> str:
    """
    Deterministic, conservative template. No thresholds are invented.
    """
    ref = ""
    if residual_risk_doc is not None:
        ref = f"Reference: Residual Risk Evaluation (type=residual_risk, doc_id={getattr(residual_risk_doc, 'id', '')}, status={getattr(residual_risk_doc, 'status', '')}, version=v{getattr(residual_risk_doc, 'version', '')})"
    else:
        ref = "Reference: Residual Risk Evaluation (type=residual_risk) — (not present yet)"

    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    return (
        "Risk Acceptability Criteria — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        f"Device description (from profile): {device_desc or 'TBD'}\n"
        f"Intended use (from profile): {intended_use or 'TBD'}\n"
        "\n"
        "Purpose\n"
        "- Define how the project determines whether risks are acceptable.\n"
        "- This document provides placeholders and must be reviewed and approved by the team.\n"
        "\n"
        "1. Concept of Risk Acceptability\n"
        "- Risk acceptability describes the criteria used to decide whether a risk is acceptable, tolerable with controls, or unacceptable.\n"
        "- Acceptability should consider severity of harm, probability of occurrence, and the effectiveness of risk control measures.\n"
        "\n"
        "2. Criteria Types (placeholders)\n"
        "- Qualitative criteria: (e.g., categories such as acceptable / ALARP / unacceptable) — TBD by the team.\n"
        "- Quantitative criteria: (e.g., numerical thresholds for risk indices) — TBD by the team.\n"
        "- Important: SmartQS does NOT invent thresholds. Enter approved thresholds here.\n"
        "\n"
        "3. Application to Residual Risk Evaluation\n"
        f"- {ref}\n"
        "- Residual risks shall be evaluated against the criteria defined in this document.\n"
        "\n"
        "4. References\n"
        "- ISO 14971: Risk management for medical devices (project/team to specify edition).\n"
        "- Project Risk Management Plan (type=rmp).\n"
    )


def _draft_benefit_risk_analysis(*, project_id: str, profile: Any, residual_risk_doc: Any) -> str:
    """
    Structure-only template (16-section Benefit–Risk Analysis Report format). No decisions or conclusions.
    """
    ref = ""
    if residual_risk_doc is not None:
        ref = f"Reference: Residual Risk Evaluation (type=residual_risk, doc_id={getattr(residual_risk_doc, 'id', '')}, status={getattr(residual_risk_doc, 'status', '')}, version=v{getattr(residual_risk_doc, 'version', '')})"
    else:
        ref = "Reference: Residual Risk Evaluation (type=residual_risk) — (not present yet)"

    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    return (
        "# Benefit–Risk Analysis Report\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic) — structure only. No conclusions or acceptability statements.\n"
        "The benefit–risk decision must be made explicitly by the project team.\n"
        "\n"
        "## 1. Document Information\n"
        f"- Project Name: (TBD)\n"
        f"- Project ID: {project_id}\n"
        "- Device Name: (TBD)\n"
        f"- Device Description: {device_desc or 'TBD'}\n"
        f"- Intended Use / Indications: {intended_use or 'TBD'}\n"
        "- Risk Management File Reference: (TBD)\n"
        "- Version: 0.1\n"
        "- Date: (TBD)\n"
        "- Author(s): (TBD)\n"
        "- Reviewer(s): (TBD)\n"
        "- Approver(s): (TBD)\n"
        "\n"
        "---\n\n"
        "## 2. Purpose\n"
        "This document provides a structured evaluation of whether the overall residual risks associated with the device are acceptable when weighed against the anticipated clinical benefits, in accordance with ISO 14971.\n"
        "\n"
        "---\n\n"
        "## 3. Scope\n"
        "This analysis applies to: final design configuration of the device; approved risk management documentation; intended use population.\n"
        "\n"
        "---\n\n"
        "## 4. Reference Documents\n"
        "- Risk Management Plan\n"
        "- Hazard Analysis / FMEA\n"
        "- Risk Control Measures Documentation\n"
        "- Residual Risk Evaluation Report\n"
        f"- {ref}\n"
        "- Clinical Evaluation Report (CER) / Literature Review\n"
        "- Usability Engineering File (if applicable)\n"
        "- Post-Market Surveillance Plan\n"
        "\n"
        "---\n\n"
        "## 5. Device Overview\n"
        "### 5.1 Device Description\n"
        f"{device_desc or '[TBD]'}\n"
        "\n"
        "### 5.2 Intended Use\n"
        f"{intended_use or '[TBD]'}\n"
        "\n"
        "### 5.3 Target Population\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 6. Summary of Residual Risks\n"
        "### 6.1 Residual Risk Evaluation Summary\n"
        "(TBD — populate from approved residual risk evaluation)\n"
        "\n"
        "### 6.2 Top Residual Risks\n"
        "| Hazard | Sequence of Events | Harm | Severity | Probability | Risk Control Measures | Residual Risk |\n"
        "|--------|------------------|------|----------|------------|----------------------|---------------|\n"
        "| (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) | (TBD) |\n"
        "\n"
        "### 6.3 Risk Control Effectiveness\n"
        "- Design controls: (TBD)\n"
        "- Protective measures: (TBD)\n"
        "- Information for safety: (TBD)\n"
        "\n"
        "### 6.4 Overall Residual Risk Statement\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 7. Anticipated Clinical Benefits\n"
        "### 7.1 Primary Clinical Benefits\n"
        "(TBD)\n"
        "\n"
        "### 7.2 Secondary Benefits\n"
        "(TBD)\n"
        "\n"
        "### 7.3 Quantification of Benefits\n"
        "(TBD)\n"
        "\n"
        "### 7.4 Time to Benefit\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 8. Benefit–Risk Comparison\n"
        "### 8.1 Qualitative Comparison\n"
        "| Category | Benefits | Risks |\n"
        "|----------|--------|------|\n"
        "| Severity | (TBD) | (TBD) |\n"
        "| Probability | (TBD) | (TBD) |\n"
        "| Duration | (TBD) | (TBD) |\n"
        "| Reversibility | (TBD) | (TBD) |\n"
        "\n"
        "### 8.2 Quantitative Comparison (if applicable)\n"
        "(TBD)\n"
        "\n"
        "### 8.3 Key Considerations\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 9. State of the Art Comparison\n"
        "### 9.1 Existing Alternatives\n"
        "(TBD)\n"
        "\n"
        "### 9.2 Comparison to Current Standard of Care\n"
        "(TBD)\n"
        "\n"
        "### 9.3 No-Treatment Scenario\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 10. Target Population Considerations\n"
        "### 10.1 High-Risk Subpopulations\n"
        "(TBD)\n"
        "\n"
        "### 10.2 Use Limitations\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 11. Uncertainty and Data Gaps\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 12. Post-Market Surveillance Plan\n"
        "### 12.1 Monitoring Activities\n"
        "(TBD)\n"
        "\n"
        "### 12.2 PMCF Activities (if applicable)\n"
        "(TBD)\n"
        "\n"
        "### 12.3 Reassessment Triggers\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 13. Overall Benefit–Risk Conclusion\n"
        "### 13.1 Statement of Acceptability\n"
        "(Intentionally left blank — requires explicit team input and approval.)\n"
        "\n"
        "### 13.2 Conditions of Acceptability\n"
        "(TBD)\n"
        "\n"
        "### 13.3 Risk–Benefit Determination Basis\n"
        "(TBD)\n"
        "\n"
        "---\n\n"
        "## 14. Traceability\n"
        "| Element | Source Document |\n"
        "|--------|----------------|\n"
        "| Hazards | Hazard Analysis |\n"
        "| Risk Controls | Risk Management File |\n"
        "| Residual Risks | Residual Risk Evaluation |\n"
        "| Clinical Benefits | Clinical Evaluation |\n"
        "| Conclusions | This Report |\n"
        "\n"
        "---\n\n"
        "## 15. Approval\n"
        "| Role | Name | Signature | Date |\n"
        "|------|------|----------|------|\n"
        "| Author | (TBD) | | |\n"
        "| Reviewer | (TBD) | | |\n"
        "| Approver | (TBD) | | |\n"
        "\n"
        "---\n\n"
        "## 16. Revision History\n"
        "| Version | Date | Description of Change | Author |\n"
        "|--------|------|----------------------|--------|\n"
        "| 0.1 | (TBD) | Initial draft | (TBD) |\n"
    )


def _draft_risk_management_review(
    *,
    project_id: str,
    profile: Any,
    artifacts: dict[str, Any],
) -> str:
    """
    Meeting-style review template. No implied approval, no auto-date/signatures.
    """
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""

    def _fmt_art(label: str, doc: Any) -> str:
        if not doc:
            return f"- {label}: (not present yet)"
        return (
            f"- {label}: doc_id={getattr(doc, 'id', '')} "
            f"(type={getattr(doc, 'type', '')}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"
        )

    reviewed_lines = [
        _fmt_art("Risk Management Plan (RMP)", artifacts.get("rmp")),
        _fmt_art("Hazard Analysis", artifacts.get("hazard_analysis")),
        _fmt_art("FMEA", artifacts.get("fmea")),
        _fmt_art("Risk Control Measures Documentation", artifacts.get("risk_controls_doc")),
        _fmt_art("Residual Risk Evaluation", artifacts.get("residual_risk")),
        _fmt_art("Risk Acceptability Criteria", artifacts.get("risk_acceptability_criteria")),
        _fmt_art("Benefit–Risk Analysis", artifacts.get("benefit_risk_analysis")),
        _fmt_art("Traceability Matrix", artifacts.get("traceability_matrix")),
    ]

    return (
        "Risk Management Review — Draft\n"
        "\n"
        "SYSTEM-GENERATED DRAFT (deterministic)\n"
        f"Project ID: {project_id}\n"
        f"Device description (from profile): {device_desc or 'TBD'}\n"
        f"Intended use (from profile): {intended_use or 'TBD'}\n"
        "\n"
        "Meeting Details\n"
        "- Date: (TBD — entered by the team)\n"
        "- Attendees: (TBD — entered by the team)\n"
        "- Chair/Facilitator: (TBD)\n"
        "\n"
        "Reviewed Artifacts (auto-referenced; presence/status only)\n"
        + "\n".join(reviewed_lines)
        + "\n\n"
        "Summary of Findings (placeholders)\n"
        "- (TBD — summarize key findings, gaps, and changes since last review)\n"
        "\n"
        "Actions / Decisions (placeholders)\n"
        "- (TBD — record action items, owners, due dates; no implied approval)\n"
        "\n"
        "Signatures / Approvals\n"
        "- (Intentionally blank — approvals must be recorded explicitly.)\n"
    )


def _should_populate(doc: Document) -> bool:
    """
    Populate only if the document is empty/placeholder OR explicitly marked Not started.
    Never overwrite otherwise.
    """
    return _status_is_not_started(doc.status) or _content_is_placeholder_for_type((doc.type or "").lower(), doc.content)


def _normalize_tags(tags: Any) -> List[str]:
    if not tags:
        return []
    if isinstance(tags, list):
        return [str(x).strip() for x in tags if str(x).strip()]
    if isinstance(tags, dict):
        vals: List[str] = []
        for v in tags.values():
            if v is None:
                continue
            if isinstance(v, list):
                vals.extend([str(x).strip() for x in v if str(x).strip()])
            else:
                vals.append(str(v).strip())
        return [x for x in vals if x]
    s = str(tags).strip()
    return [s] if s else []


def _is_pacemaker_context(profile: Any, components: list[Any]) -> bool:
    """
    Lightweight heuristic to decide whether to use implantable-cardiac (pacemaker-like)
    templates. Deterministic and purely based on user-entered context.
    """
    blob = " ".join(
        [
            str(getattr(profile, "intended_use", "") or ""),
            str(getattr(profile, "device_description", "") or ""),
            " ".join([str(getattr(c, "name", "") or "") for c in components]),
        ]
    ).lower()
    keywords = [
        "pacemaker",
        "cardiac",
        "bradycardia",
        "arrhythmia",
        "implant",
        "implantable",
        "pacing",
        "lead",
        "electrode",
        "telemetry",
    ]
    return any(k in blob for k in keywords)


def _traceability_header(*, project_id: str, profile: Any) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    return (
        "DRAFT — Generated from Project Setup (ProjectProfile + Components)\n"
        "DRAFT — Generated deterministically from ProjectProfile + Components\n"
        f"Project ID: {project_id}\n"
        f"Device description: {device_desc or 'TBD'}\n"
        f"Intended use: {intended_use or 'TBD'}\n"
        f"User population: {user_pop or 'TBD'}\n"
        f"Use environment: {use_env or 'TBD'}\n"
    )


def _draft_rmp(*, project_id: str, profile: Any, components: list[Any]) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    user_pop = (getattr(profile, "user_population", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""

    comp_lines = []
    for c in components:
        comp_lines.append(f"- {c.name}{(': ' + c.description) if getattr(c, 'description', None) else ''}")
    if not comp_lines:
        comp_lines = ["- (No components defined yet)"]

    return (
        "Risk Management Plan (RMP) — Draft\n"
        "\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "1. Purpose and Scope\n"
        "- This Risk Management Plan defines the planned activities and responsibilities for risk management.\n"
        "- This draft is intended to be reviewed and tailored to the project.\n"
        "\n"
        "2. Device Description and Intended Use (from project profile)\n"
        f"- Device description: {device_desc or 'TBD'}\n"
        f"- Intended use: {intended_use or 'TBD'}\n"
        f"- User population: {user_pop or 'TBD'}\n"
        f"- Use environment: {use_env or 'TBD'}\n"
        "\n"
        "3. System / Components in Scope (from project components)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "4. Risk Management Process (draft)\n"
        "- Planned activities: hazard identification, risk estimation, risk evaluation, risk control, and evaluation of residual risk.\n"
        "- Risk control verification and production/post-production information shall be considered.\n"
        "- Note: This draft does not assign risk scores; scoring criteria should be defined and approved by the team.\n"
        "\n"
        "5. Roles and Responsibilities (draft)\n"
        "- Risk Management Lead: maintains this plan and ensures execution.\n"
        "- Design Engineering: provides design information and implements risk controls.\n"
        "- Quality / Regulatory: ensures process alignment and review support.\n"
        "- Clinical / Safety: supports hazard identification and clinical rationale.\n"
        "\n"
        "6. Review / Approval\n"
        "- This draft shall be reviewed and approved prior to formal use.\n"
    )


def _draft_hazard_analysis(*, project_id: str, profile: Any, components: list[Any]) -> str:
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""

    is_pace = _is_pacemaker_context(profile, components)
    header = (
        "Hazard Analysis — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Important\n"
        "- DRAFT content. Deterministic starter hazards only.\n"
        "- No risk scoring is assigned in this draft.\n"
        "- Review and tailor to the specific design, intended use, and clinical context.\n\n"
    )

    if not components:
        return header + "Seeded Hazards\n- (No components defined yet. Add components to seed hazards.)\n"

    # Implantable-cardiac (pacemaker-like) hazard categories + component mapping.
    categories = [
        ("Electrical / Energy Delivery", ["power", "battery", "capacitor", "charger", "supply", "energy"]),
        ("Sensing / Detection", ["sense", "sensor", "electrode", "lead", "ecg"]),
        ("Therapy Delivery (Pacing Output)", ["pace", "output", "pulse", "stim"]),
        ("Software / Firmware / Algorithms", ["software", "firmware", "algorithm", "code", "app", "os"]),
        ("Cybersecurity / Connectivity", ["telemetry", "wireless", "rf", "bluetooth", "wifi", "cloud", "cyber"]),
        ("Mechanical / Structural", ["housing", "case", "seal", "connector", "header", "mechanical"]),
        ("Biological / Biocompatibility", ["bio", "tissue", "coating", "material", "sterile", "implant"]),
        ("EMI / Environmental", ["emi", "emc", "mri", "magnet", "environment"]),
        ("Usability / Human Factors / Clinical Workflow", ["user", "clinician", "procedure", "implantation", "programmer"]),
    ]

    def classify_component(c: Any) -> str:
        name = (getattr(c, "name", "") or "").lower()
        tags = " ".join(_normalize_tags(getattr(c, "tags", None))).lower()
        blob = f"{name} {tags}"
        for cat, hints in categories:
            if any(h in blob for h in hints):
                return cat
        return "General (System-level)"

    # Build per-category hazards, linked to components, with no scoring.
    grouped: Dict[str, List[Any]] = {}
    for c in components:
        cat = classify_component(c) if is_pace else "General (System-level)"
        grouped.setdefault(cat, []).append(c)

    # Deterministic ordering for stable drafts.
    for cat in list(grouped.keys()):
        grouped[cat] = sorted(grouped[cat], key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")))

    lines: List[str] = []
    lines.append("Seeded Hazard Categories and Hazards")
    lines.append(f"- Device context template: {'Implantable cardiac (pacemaker-like)' if is_pace else 'Generic medical device'}")
    lines.append("")

    def hazard_block(component_name: str, category: str) -> str:
        # Keep wording neutral and avoid implying quantified risk.
        return (
            f"Component: {component_name}\n"
            f"Category: {category}\n"
            f"Hazard (Draft): Potential harm due to {component_name} malfunction or misuse\n"
            f"Hazardous situation (Draft): During {intended_use or 'intended use'}, in {use_env or 'the intended environment'}, "
            f"{component_name} may fail, degrade, or behave unexpectedly.\n"
            "Possible harms (Draft): Injury to patient/user, therapy interruption, inappropriate therapy, infection, or other clinically relevant harm.\n"
            "Risk scoring: Not assigned in this draft.\n"
        )

    for cat in sorted(grouped.keys()):
        lines.append(f"\n== {cat} ==")
        for c in grouped[cat]:
            lines.append(hazard_block(c.name, cat))

    return header + "\n".join(lines).strip() + "\n"


def _draft_rmf_scaffold(*, project_id: str, profile: Any, components: list[Any]) -> str:
    """
    Deterministic RMF scaffold (structure only).
    RMF is typically a compilation of RMP + hazard analysis + risk analysis (incl. FMEA) + risk controls + residual risk + traceability.
    """
    comp_lines = [f"- {c.name} (id={getattr(c, 'id', '')})" for c in components] or ["- (No components defined yet)"]
    return (
        "Risk Management File (RMF/RMR) — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Overview\n"
        "- This is a DRAFT RMF structure generated from Project Setup.\n"
        "- It is a compilation shell; expand/verify before use.\n\n"
        "1. Device Overview\n"
        "- Device description: (from profile)\n"
        "- Intended use: (from profile)\n"
        "- User population: (from profile)\n"
        "- Use environment: (from profile)\n\n"
        "2. Components / System Breakdown (from project components)\n"
        + "\n".join(comp_lines)
        + "\n\n"
        "3. Risk Management Plan (RMP) Summary\n"
        "- (Draft summary to be generated)\n\n"
        "4. Hazard Identification / Hazard Analysis Summary\n"
        "- (Draft summary to be generated)\n\n"
        "5. Risk Analysis Summary (including FMEA)\n"
        "- (Draft summary to be generated)\n\n"
        "6. Risk Control Measures Summary\n"
        "- (Draft summary to be generated)\n\n"
        "7. Residual Risk Evaluation Summary\n"
        "- (Draft summary to be generated)\n\n"
        "8. Traceability Summary\n"
        "- (Draft summary to be generated)\n\n"
        "9. Production and Post-Production Information (PMS)\n"
        "- (Placeholders; do not treat as executed evidence)\n\n"
        "10. Review and Approval\n"
        "- Approvals: TBD\n"
    )


def _ensure_fmea_rows_for_components(db: Session, *, project_id: str, components: list[Any]) -> int:
    existing = db.query(FMEARow).filter(FMEARow.project_id == project_id).count()
    if existing > 0:
        return 0
    if not components:
        return 0

    created = 0
    # Deterministic order
    for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
        fmea_crud.create_fmea_row(
            db,
            FMEARowCreate(
                project_id=project_id,
                component_id=c.id,
                # Draft placeholders; do not assign risk scores.
                failure_mode=f"[DRAFT] {c.name} — placeholder failure mode (to be refined)",
                effect="[DRAFT] Placeholder effect on therapy/system/user (to be refined)",
                cause="[DRAFT] Placeholder cause / mechanism (to be refined)",
                severity=None,
                probability=None,
                detection=None,
                mitigation="[DRAFT] Placeholder mitigation / control (to be refined)",
                ai_metadata={
                    "seeded_by": "initialize_from_profile",
                    "project_id": project_id,
                    "component_name": c.name,
                    "draft": True,
                },
            ),
        )
        created += 1
    return created


def _draft_fmea_table(db: Session, *, project_id: str, components: list[Any]) -> str:
    """
    Deterministic text table for the FMEA document draft.
    We keep it plain text to avoid time-based HTML differences and keep idempotency stable.
    """
    comp_name_by_id = {str(getattr(c, "id", "")): str(getattr(c, "name", "") or "") for c in components}
    rows = db.query(FMEARow).filter(FMEARow.project_id == project_id).all()
    if not rows:
        if not components:
            return (
                "FMEA — Draft\n\n"
                + _traceability_header(project_id=project_id, profile=None)
                + "\nNo components defined yet. Add components to seed starter FMEA rows.\n"
            )
        return (
            "FMEA — Draft\n\n"
            + _traceability_header(project_id=project_id, profile=None)
            + "\nNo FMEA rows exist yet.\n"
        )

    lines = [
        "FMEA — Draft",
        "",
        "Important",
        "- Do not treat as validated risk analysis.",
        "- Scores may be blank until generated and/or reviewed.",
        "",
        f"Project ID: {project_id}",
        "",
        "Seeded starter rows (one per component):",
        "",
        "component | hazard | failure_mode | effect | cause | S | O | D | mitigation",
        "-" * 120,
    ]
    # Deterministic ordering
    for r in sorted(rows, key=lambda x: (str(x.component_id or ""), str(x.id or ""))):
        comp_label = comp_name_by_id.get(str(r.component_id or ""), "") or (str(r.component_id or "")[:8] if r.component_id else "")
        hazard = ""
        try:
            if isinstance(getattr(r, "ai_metadata", None), dict):
                hazard = str(r.ai_metadata.get("hazard") or "").strip()
        except Exception:
            hazard = ""
        lines.append(
            f"{comp_label} | {hazard} | {r.failure_mode or ''} | {r.effect or ''} | {r.cause or ''} | "
            f"{'' if r.severity is None else r.severity} | {'' if r.probability is None else r.probability} | {'' if r.detection is None else r.detection} | {r.mitigation or ''}"
        )
    return "\n".join(lines) + "\n"


def _slug(s: str) -> str:
    out = []
    for ch in (s or ""):
        if ch.isalnum():
            out.append(ch.upper())
    return "".join(out)[:10] or "COMP"


def _build_design_inputs(
    *, project_id: str, profile: Any, components: list[Any]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, design_inputs) where design_inputs is a list of:
      {id, component_id, component_name, text}
    """
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    ksc = getattr(profile, "key_safety_characteristics", None) if profile else None
    ksc_list = [str(x).strip() for x in (ksc or []) if str(x).strip()] if isinstance(ksc, list) else []

    comps = sorted(
        components,
        key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")),
    )

    di_entries: list[dict[str, str]] = []
    lines: list[str] = [
        "Design Inputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Draft, deterministic design inputs derived from Project Setup data.",
        "- Use these as traceability scaffolding; refine into verifiable requirements and acceptance criteria.",
        "",
        "Design Inputs (Draft)",
    ]

    if not comps:
        lines.append("- (No components defined yet.)")
        return "\n".join(lines) + "\n", di_entries

    safety_hint = "; ".join(ksc_list[:5]) if ksc_list else ""
    if safety_hint:
        lines.append(f"Key safety characteristics (from setup): {safety_hint}")
        lines.append("")

    for comp in comps:
        cname = str(getattr(comp, "name", "") or "").strip() or "Component"
        cid = str(getattr(comp, "id", "") or "")
        slug = _slug(cname)

        # Always 3, add up to 2 more derived from safety characteristics.
        base_texts = [
            f"The device shall provide the required function for {cname} as part of {device_desc or 'the device'} for {intended_use or 'the intended use'}. [DRAFT]",
            f"The device shall detect and handle foreseeable faults related to {cname} to maintain a safe state. [DRAFT]",
            f"The device shall support verification of {cname} requirements through defined acceptance criteria (TBD). [DRAFT]",
        ]
        extra_texts: list[str] = []
        for k in ksc_list:
            if len(extra_texts) >= 2:
                break
            extra_texts.append(f"The device shall address safety characteristic '{k}' with respect to {cname}. [DRAFT]")

        texts = base_texts + extra_texts
        texts = texts[:5]

        lines.append(f"\nComponent: {cname} (component_id={cid})")
        for i, txt in enumerate(texts, start=1):
            di_id = f"DI-{slug}-{i:02d}"
            lines.append(f"- {di_id}: {txt}")
            di_entries.append(
                {
                    "id": di_id,
                    "component_id": cid,
                    "component_name": cname,
                    "text": txt,
                }
            )

    return "\n".join(lines).strip() + "\n", di_entries


def _build_design_outputs(
    *, project_id: str, profile: Any, design_inputs: list[dict[str, str]]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, design_outputs) where design_outputs entries are:
      {id, input_id, text}
    """
    lines: list[str] = [
        "Design Outputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Draft, deterministic design outputs mapped to Design Inputs.",
        "- Outputs are placeholders to scaffold traceability; replace with real artifacts (drawings, schematics, code, specs).",
        "",
        "Design Outputs (Draft)",
    ]

    do_entries: list[dict[str, str]] = []
    if not design_inputs:
        lines.append("- (No Design Inputs available yet. Generate Design Inputs first.)")
        return "\n".join(lines) + "\n", do_entries

    for di in design_inputs:
        di_id = di["id"]
        do_id = di_id.replace("DI-", "DO-", 1)
        text = f"Design output to be defined for {di_id} (e.g., specification, schematic, software module, drawing). [DRAFT]"
        lines.append(f"- {do_id} (maps to {di_id}): {text}")
        do_entries.append({"id": do_id, "input_id": di_id, "text": text})

    return "\n".join(lines).strip() + "\n", do_entries


def _build_vv_plan(
    db: Session, *, project_id: str, profile: Any, design_inputs: list[dict[str, str]]
) -> tuple[str, list[dict[str, str]]]:
    """
    Returns (content, vv_items) where vv_items are structured plan activities:
      - For Design Inputs: {id, source_type, input_id, source_ref, verification_method, acceptance_criteria, planned_evidence, status}
      - For Risk Controls: {id, source_type, risk_control_id, source_ref, verification_method, acceptance_criteria, planned_evidence, status}
    """
    lines: list[str] = [
        "V&V Plan — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose and Scope (Draft)",
        "- This plan defines the intended verification and validation strategy for the project.\n"
        "- It is a structure-first scaffold and does not imply execution, completion, or compliance.\n",
        "Definitions (Draft)",
        "- Verification: confirmation, through provision of objective evidence, that specified requirements have been fulfilled.",
        "- Validation: confirmation that the device meets user needs and intended use under actual or simulated use conditions.",
        "",
        "Strategy (Draft)",
        "- Verification methods may include inspection, analysis, testing, and demonstration.",
        "- Validation activities should evaluate intended use, use environment, and user population.",
        "",
        "Traceability Expectations (Draft)",
        "- Each Design Input shall map to at least one verification activity and associated evidence.",
        "- Risk controls with defined verification methods should map to planned activities and evidence.",
        "- This draft does not assert compliance or acceptance; it establishes placeholders only.",
        "",
        "Planned Verification Activities (Draft; Status = Planned)",
    ]

    vv_items: list[dict[str, str]] = []
    seq = 1

    # A) Risk Controls (structured) with verification_method
    try:
        from models.risk_control import RiskControl

        controls = (
            db.query(RiskControl)
            .filter(RiskControl.project_id == project_id)
            .all()
        )
        controls = [
            c
            for c in controls
            if str(getattr(c, "verification_method", "") or "").strip()
        ]
        # Deterministic ordering
        controls = sorted(controls, key=lambda c: (str(getattr(c, "control_key", "") or ""), str(getattr(c, "id", "") or "")))
        if controls:
            lines.append("")
            lines.append("A) Planned activities from Risk Controls (verification_method present)")
            for rc in controls:
                vv_id = f"VV-{seq:03d}"
                seq += 1
                rc_key = (getattr(rc, "control_key", None) or f"RC-{str(getattr(rc, 'id', '') or '')[:8]}")
                rc_name = (getattr(rc, "control_name", None) or "").strip() or "Risk Control"
                method = (getattr(rc, "verification_method", None) or "").strip()
                vv_items.append(
                    {
                        "id": vv_id,
                        "source_type": "Risk Control",
                        "risk_control_id": str(getattr(rc, "id", "") or ""),
                        "source_ref": f"{rc_key} — {rc_name}",
                        "verification_method": method,
                        "acceptance_criteria": "TBD",
                        "planned_evidence": f"DV Test Report: {vv_id} (TBD)",
                        "status": "Planned",
                    }
                )
                lines.append(f"- {vv_id}")
                lines.append(f"  - Source type: Risk Control")
                lines.append(f"  - Source reference: {rc_key} — {rc_name} (risk_control_id={rc.id})")
                lines.append(f"  - Verification method: {method}")
                lines.append(f"  - Acceptance criteria: TBD")
                lines.append(f"  - Planned evidence artifact: DV Test Report: {vv_id} (TBD)")
                lines.append(f"  - Status: Planned")
    except Exception:
        # Keep robust in environments where tables may not exist yet.
        pass

    # B) Design Inputs (placeholders per input)
    if design_inputs:
        lines.append("")
        lines.append("B) Planned activities from Design Inputs (placeholders)")
        for di in design_inputs:
            di_id = str(di.get("id") or "")
            vv_id = f"VV-{seq:03d}"
            seq += 1
            vv_items.append(
                {
                    "id": vv_id,
                    "source_type": "Design Input",
                    "input_id": di_id,
                    "source_ref": di_id,
                    "verification_method": "TBD (Test/Analysis/Inspection)",
                    "acceptance_criteria": "TBD",
                    "planned_evidence": f"DV Test Report: {vv_id} (TBD)",
                    "status": "Planned",
                }
            )
            lines.append(f"- {vv_id}")
            lines.append(f"  - Source type: Design Input")
            lines.append(f"  - Source reference: {di_id}")
            lines.append(f"  - Verification method: TBD (Test/Analysis/Inspection)")
            lines.append(f"  - Acceptance criteria: TBD")
            lines.append(f"  - Planned evidence artifact: DV Test Report: {vv_id} (TBD)")
            lines.append(f"  - Status: Planned")
    else:
        lines.append("")
        lines.append("B) Planned activities from Design Inputs")
        lines.append("- (No Design Inputs available yet.)")

    return "\n".join(lines).strip() + "\n", vv_items


def _build_vv_evidence_report(
    *, project_id: str, profile: Any, vv_items: list[dict[str, str]]
) -> str:
    lines: list[str] = [
        "V&V Evidence Report — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "NOT EXECUTED — DRAFT SCAFFOLD",
        "- This report is a draft scaffold. Evidence must be uploaded/linked and execution recorded.",
        "- Nothing in this document implies that tests were executed or passed.",
        "",
        "Evidence Slots (mirrors V&V Plan activities)",
    ]
    if not vv_items:
        lines.append("- (No V&V Plan placeholders available yet.)")
        return "\n".join(lines).strip() + "\n"

    for item in vv_items:
        vv_id = str(item.get("id") or "")
        source_type = str(item.get("source_type") or "Unknown")
        source_ref = str(item.get("source_ref") or "")
        lines.append(f"\nEvidence Slot: {vv_id}")
        lines.append(f"- Activity reference: {vv_id}")
        lines.append(f"- Source type: {source_type}")
        lines.append(f"- Source reference: {source_ref}")
        lines.append("- Evidence expected (placeholder title): (TBD)")
        lines.append("- Evidence link/file reference: (empty)")
        lines.append("- Result summary: (empty)")
        lines.append("- Deviations/notes: (empty)")
        lines.append("- Status: Not Executed")

    return "\n".join(lines).strip() + "\n"


def _build_risk_controls_doc(db: Session, *, project_id: str, profile: Any, components: list[Any]) -> str:
    comps = sorted(
        components,
        key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or "")),
    )
    lines: list[str] = [
        "Risk Control Measures Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Note",
        "- Draft structure only. Effectiveness assessment is intentionally left empty.",
        "",
    ]
    comp_name_by_id = {str(getattr(c, "id", "") or ""): str(getattr(c, "name", "") or "") for c in comps}

    # Gather structured RiskControls (preferred) + RiskItem free-text + FMEA mitigation as fallback.
    risk_items = db.query(RiskItem).filter(RiskItem.project_id == project_id).all()
    controls = db.query(RiskControl).filter(RiskControl.project_id == project_id).all()
    controls_by_risk_item: Dict[str, List[RiskControl]] = {}
    for rc in controls:
        controls_by_risk_item.setdefault(str(rc.risk_item_id), []).append(rc)

    # FMEA mitigation fallback
    fmea_rows = fmea_crud.get_fmea_rows_by_project(db, project_id)

    grouped: Dict[str, List[Dict[str, Any]]] = {}

    def add_entry(component_name: str, entry: Dict[str, Any]):
        grouped.setdefault(component_name or "Unknown", []).append(entry)

    # 1) Structured RiskControls, grouped by component_name from RiskItem/component fields
    for ri in risk_items:
        cname = (getattr(ri, "component_name", None) or comp_name_by_id.get(str(getattr(ri, "component_id", "") or ""), "") or "Unknown").strip()
        rcs = controls_by_risk_item.get(str(ri.id), [])
        if rcs:
            for rc in rcs:
                add_entry(
                    cname,
                    {
                        "source": "RiskControl",
                        "risk_key": getattr(ri, "risk_key", None) or f"R-{str(ri.id)[:8]}",
                        "control_key": getattr(rc, "control_key", None) or f"RC-{str(rc.id)[:8]}",
                        "control_name": getattr(rc, "control_name", None),
                        "control_description": getattr(rc, "control_description", None),
                        "control_type": getattr(rc, "control_type", None) or "TBD",
                        "verification_method": getattr(rc, "verification_method", None) or "TBD",
                        "effectiveness": getattr(rc, "effectiveness_notes", None) or "(blank)",
                    },
                )
        else:
            # 2) Free-text controls on RiskItem (existing data, but not structured yet)
            txts = []
            if getattr(ri, "mitigation_strategy", None):
                txts.append(("Mitigation strategy", str(ri.mitigation_strategy)))
            if getattr(ri, "control_measures", None):
                txts.append(("Control measures", str(ri.control_measures)))
            for label, txt in txts:
                if not (txt or "").strip():
                    continue
                add_entry(
                    cname,
                    {
                        "source": "RiskItem",
                        "risk_key": getattr(ri, "risk_key", None) or f"R-{str(ri.id)[:8]}",
                        "control_key": f"{label.replace(' ', '_').upper()}-{str(ri.id)[:8]}",
                        "control_name": f"{label} (from Risk Item)",
                        "control_description": txt.strip(),
                        "control_type": "TBD",
                        "verification_method": "TBD",
                        "effectiveness": "(blank)",
                    },
                )

    # 3) FMEA mitigation fallback controls
    for r in fmea_rows:
        mit = (getattr(r, "mitigation", None) or "").strip()
        if not mit:
            continue
        cid = str(getattr(r, "component_id", "") or "")
        cname = comp_name_by_id.get(cid, "") or "Unknown"
        add_entry(
            cname,
            {
                "source": "FMEA",
                "risk_key": f"FMEA-{str(r.id)[:8]}",
                "control_key": f"FMEA-MIT-{str(r.id)[:8]}",
                "control_name": "Mitigation (from FMEA row)",
                "control_description": mit,
                "control_type": "TBD",
                "verification_method": "TBD",
                "effectiveness": "(blank)",
            },
        )

    if not grouped:
        lines.append("(No risk controls found yet. Add Risk Controls or enter mitigations on FMEA rows.)")
        return "\n".join(lines).strip() + "\n"

    # Deterministic ordering for stable drafts
    for component_name in sorted(grouped.keys(), key=lambda x: (x or "").lower()):
        lines.append(f"\nComponent: {component_name}")
        lines.append("Controls (aggregated from existing data)")
        for e in grouped[component_name]:
            lines.append(
                f"- {e.get('control_key')}: {e.get('control_name')} "
                f"(source={e.get('source')}, risk={e.get('risk_key')})"
            )
            lines.append(f"  - Description: {e.get('control_description') or 'TBD'}")
            lines.append(f"  - Control type (inherent/protective/information): {e.get('control_type') or 'TBD'}")
            lines.append(f"  - Verification method: {e.get('verification_method') or 'TBD'}")
            lines.append(f"  - Effectiveness: {e.get('effectiveness') or '(blank)'}")

    return "\n".join(lines).strip() + "\n"


def _build_residual_risk_eval(*, project_id: str, profile: Any) -> str:
    return (
        "Residual Risk Evaluation — Draft\n\n"
        + _traceability_header(project_id=project_id, profile=profile)
        + "\n"
        "Structure\n"
        "- This draft provides placeholders only; no risk scoring is assigned.\n\n"
        "1) Pre-control risk summary (placeholder)\n"
        "- Summary: TBD [DRAFT]\n\n"
        "2) Post-control (residual) risk summary (placeholder)\n"
        "- Summary: TBD [DRAFT]\n\n"
        "3) Acceptability decision (placeholder)\n"
        "- Criteria applied: TBD [DRAFT]\n"
        "- Decision: TBD [DRAFT]\n"
        "- Rationale: TBD [DRAFT]\n"
    )


def _build_traceability_matrix(
    *,
    project_id: str,
    profile: Any,
    components: list[Any],
    design_inputs: list[dict[str, str]],
    design_outputs: list[dict[str, str]],
    vv_items: list[dict[str, str]],
    fmea_rows: list[FMEARow],
) -> str:
    # Component -> FMEA linkage summary
    fmea_by_comp: Dict[str, int] = {}
    for r in fmea_rows:
        cid = str(r.component_id or "")
        fmea_by_comp[cid] = fmea_by_comp.get(cid, 0) + 1

    lines: list[str] = [
        "Traceability Matrix — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Important",
        "- Draft trace links generated from Project Setup scaffolding.",
        "- No compliance claims are made in this draft.",
        "",
        "A) Components → FMEA Rows",
        "component_id | component_name | fmea_rows_count",
        "-" * 72,
    ]
    for c in sorted(components, key=lambda x: (str(getattr(x, 'name', '') or '').lower(), str(getattr(x, 'id', '') or ''))):
        cid = str(getattr(c, "id", "") or "")
        cname = str(getattr(c, "name", "") or "")
        lines.append(f"{cid} | {cname} | {fmea_by_comp.get(cid, 0)}")

    # DI -> DO -> VV (Design Input sourced activities only)
    do_by_input = {d["input_id"]: d["id"] for d in design_outputs}
    vv_by_input: Dict[str, str] = {}
    vv_by_risk_control: Dict[str, str] = {}
    for v in vv_items:
        iid = str(v.get("input_id") or "")
        rcid = str(v.get("risk_control_id") or "")
        if iid:
            vv_by_input[iid] = str(v.get("id") or "")
        if rcid:
            vv_by_risk_control[rcid] = str(v.get("id") or "")

    lines.extend(
        [
            "",
            "B) Design Inputs → Design Outputs → V&V Plan",
            "design_input_id | design_output_id | vv_item_id",
            "-" * 72,
        ]
    )
    for di in design_inputs:
        di_id = di["id"]
        lines.append(f"{di_id} | {do_by_input.get(di_id, '')} | {vv_by_input.get(di_id, '')}")

    # Risk Control -> VV (candidates; evidence slots mirror VV IDs)
    lines.extend(
        [
            "",
            "C) Risk Controls → V&V Plan → V&V Evidence",
            "risk_control_id | vv_item_id | vv_evidence_slot_id",
            "-" * 72,
        ]
    )
    if not vv_by_risk_control:
        lines.append("(No risk-control sourced V&V activities found yet.)")
    else:
        for rcid in sorted(vv_by_risk_control.keys()):
            vvid = vv_by_risk_control.get(rcid, "")
            lines.append(f"{rcid} | {vvid} | {vvid}")

    return "\n".join(lines).strip() + "\n"
    intended_use = (getattr(profile, "intended_use", None) or "").strip() if profile else ""
    use_env = (getattr(profile, "use_environment", None) or "").strip() if profile else ""
    device_desc = (getattr(profile, "device_description", None) or "").strip() if profile else ""
    is_pace = _is_pacemaker_context(profile, components)

    lines = [
        "Design Inputs Documentation — Draft",
        "",
        _traceability_header(project_id=project_id, profile=profile).rstrip(),
        "",
        "Purpose",
        "- Deterministic starter design inputs derived from intended use + safety expectations.",
        "- This draft provides high-level inputs that must be refined into verifiable requirements and acceptance criteria.",
        "",
        f"Context summary: device={device_desc or 'TBD'}; intended_use={intended_use or 'TBD'}; use_environment={use_env or 'TBD'}",
        "",
        "Seeded High-Level Design Inputs (Draft)",
    ]

    # 5–10 high-level inputs (keep deterministic and neutral)
    inputs: List[str] = []
    base_context = f"for {intended_use or 'the intended use'} in {use_env or 'the intended environment'}"
    inputs.extend(
        [
            f"- DI-01 (Safety): The device shall be designed to minimize foreseeable harm {base_context}. [DRAFT]",
            f"- DI-02 (Performance): The device shall perform its intended function within specified limits {base_context}. [DRAFT]",
            "- DI-03 (Risk Controls): The device design shall include appropriate risk control measures and verification evidence. [DRAFT]",
            "- DI-04 (Alarms/Indicators): The device shall provide appropriate status indication for safe use (as applicable). [DRAFT]",
            "- DI-05 (Usability): The device shall support safe and effective use by the intended user population. [DRAFT]",
        ]
    )
    if is_pace:
        inputs.extend(
            [
                "- DI-06 (Therapy): The device shall deliver pacing therapy within defined output parameter tolerances. [DRAFT]",
                "- DI-07 (Sensing): The device shall reliably sense relevant cardiac signals to support correct therapy behavior. [DRAFT]",
                "- DI-08 (EMI/EMC): The device shall maintain safe behavior under reasonably foreseeable electromagnetic interference conditions. [DRAFT]",
                "- DI-09 (Longevity): The device shall meet a defined service life / battery longevity target under specified use profiles. [DRAFT]",
                "- DI-10 (Biocompatibility): Patient-contacting materials shall be biocompatible for intended duration of contact. [DRAFT]",
                "- DI-11 (Cybersecurity): The device shall incorporate security controls appropriate to its connectivity and threat model. [DRAFT]",
            ]
        )
    else:
        inputs.extend(
            [
                "- DI-06 (EMI/EMC): The device shall maintain safe behavior under reasonably foreseeable electromagnetic interference conditions. [DRAFT]",
                "- DI-07 (Software): If software is present, it shall be developed and verified commensurate with its safety impact. [DRAFT]",
                "- DI-08 (Biocompatibility): Patient-contacting materials shall be biocompatible for intended duration of contact (as applicable). [DRAFT]",
            ]
        )

    # Keep between 5 and 10 if possible; pacemaker template may add more, so trim deterministically.
    max_items = 10
    inputs = inputs[:max_items]
    lines.extend(inputs)

    if components:
        lines.append("")
        lines.append("Component Traceability (from project components)")
        for c in sorted(components, key=lambda x: (str(getattr(x, "name", "") or "").lower(), str(getattr(x, "id", "") or ""))):
            lines.append(f"- {c.name} (component_id={c.id})")
    else:
        lines.append("")
        lines.append("Component Traceability")
        lines.append("- (No components defined yet.)")

    return "\n".join(lines).strip() + "\n"


def initialize_project_from_profile(db: Session, *, project_id: str) -> Dict[str, Any]:
    """
    Controlled initializer:
    - Idempotent
    - Never overwrites non-empty/non-placeholder content unless status == Not started
    - Creates a new document version when generating content (via update_document)
    """
    stats = InitFromProfileStats()

    created = initialize_project_required_docs(db, project_id)
    stats.created_required_docs = len(created)

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    # Precompute deterministic DI/DO/VV placeholder lists for traceability scaffolding.
    di_content, di_entries = _build_design_inputs(project_id=project_id, profile=profile, components=components)
    do_content, do_entries = _build_design_outputs(project_id=project_id, profile=profile, design_inputs=di_entries)
    vv_plan_content, vv_items = _build_vv_plan(db, project_id=project_id, profile=profile, design_inputs=di_entries)

    # Convenience: current docs for cross-references (best-effort, may be None).
    def _d(t: str) -> Any:
        return by_type.get((t or "").lower())

    refs_common = {
        "design_inputs_doc": _d("design_inputs_doc"),
        "design_outputs_doc": _d("design_outputs_doc"),
        "design_reviews": _d("design_reviews"),
        "design_change_record": _d("design_change_record"),
        "hazard_analysis": _d("hazard_analysis"),
        "fmea": _d("fmea"),
        "risk_controls_doc": _d("risk_controls_doc"),
        "vv_plan": _d("vv_plan"),
        "pms_plan": _d("pms_plan"),
    }

    # 1) RMP
    rmp = by_type.get("rmp")
    if rmp and _should_populate(rmp):
        content = _draft_rmp(project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, rmp.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("rmp")

    # 2) Hazard Analysis
    ha = by_type.get("hazard_analysis")
    if ha and _should_populate(ha):
        content = _draft_hazard_analysis(project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, ha.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("hazard_analysis")

    # 3) FMEA
    fmea_doc = by_type.get("fmea")
    if fmea_doc and _should_populate(fmea_doc):
        stats.seeded_fmea_rows = _ensure_fmea_rows_for_components(db, project_id=project_id, components=components)
        content = _draft_fmea_table(db, project_id=project_id, components=components)
        document_crud.update_document(db, fmea_doc.id, DocumentUpdate(content=content, status="draft"), project_id)
        stats.updated_documents.append("fmea")

    # 4) Design Inputs doc
    di = by_type.get("design_inputs_doc")
    if di and _should_populate(di):
        document_crud.update_document(db, di.id, DocumentUpdate(content=di_content, status="draft"), project_id)
        stats.updated_documents.append("design_inputs_doc")

    # 5) Design Outputs doc
    do = by_type.get("design_outputs_doc")
    if do and _should_populate(do):
        document_crud.update_document(db, do.id, DocumentUpdate(content=do_content, status="draft"), project_id)
        stats.updated_documents.append("design_outputs_doc")

    # 5b) Design & Development Plan
    ddp = by_type.get("design_dev_plan")
    if ddp and _should_populate(ddp):
        ddp_content = _draft_design_dev_plan(project_id=project_id, profile=profile, components=components, refs=refs_common)
        document_crud.update_document(db, ddp.id, DocumentUpdate(content=ddp_content, status="draft"), project_id)
        stats.updated_documents.append("design_dev_plan")

    # 5c) Design Reviews
    dr = by_type.get("design_reviews")
    if dr and _should_populate(dr):
        dr_content = _draft_design_reviews(project_id=project_id, profile=profile, refs=refs_common)
        document_crud.update_document(db, dr.id, DocumentUpdate(content=dr_content, status="draft"), project_id)
        stats.updated_documents.append("design_reviews")

    # 5d) Design Change Record (base template; change entries appended separately via version hook)
    dcr = by_type.get("design_change_record")
    if dcr and _should_populate(dcr):
        dcr_content = _draft_design_change_record_base(project_id=project_id, profile=profile)
        document_crud.update_document(db, dcr.id, DocumentUpdate(content=dcr_content, status="draft"), project_id)
        stats.updated_documents.append("design_change_record")

    # 6) V&V Plan
    vvp = by_type.get("vv_plan")
    if vvp and _should_populate(vvp):
        document_crud.update_document(db, vvp.id, DocumentUpdate(content=vv_plan_content, status="draft"), project_id)
        stats.updated_documents.append("vv_plan")

    # 7) V&V Evidence Report
    vve = by_type.get("vv_evidence")
    if vve and _should_populate(vve):
        vve_content = _build_vv_evidence_report(project_id=project_id, profile=profile, vv_items=vv_items)
        document_crud.update_document(db, vve.id, DocumentUpdate(content=vve_content, status="draft"), project_id)
        stats.updated_documents.append("vv_evidence")

    # 7b) Validation Summary (structure only; NOT COMPLETE until evidence exists)
    vs = by_type.get("validation_summary")
    if vs and _should_populate(vs):
        # Refs are best-effort; do not imply completion.
        refreshed = document_crud.get_documents_by_project(db, project_id)
        refreshed_by_type = {(d.type or "").lower(): d for d in refreshed}
        vs_content = _build_validation_summary(
            project_id=project_id,
            profile=profile,
            vv_evidence_doc=refreshed_by_type.get("vv_evidence"),
            residual_risk_doc=refreshed_by_type.get("residual_risk"),
        )
        document_crud.update_document(db, vs.id, DocumentUpdate(content=vs_content, status="draft"), project_id)
        stats.updated_documents.append("validation_summary")

    # 8) Risk Controls Documentation
    rcd = by_type.get("risk_controls_doc")
    if rcd and _should_populate(rcd):
        rcd_content = _build_risk_controls_doc(db, project_id=project_id, profile=profile, components=components)
        document_crud.update_document(db, rcd.id, DocumentUpdate(content=rcd_content, status="draft"), project_id)
        stats.updated_documents.append("risk_controls_doc")

    # 9) Residual Risk Evaluation
    rr = by_type.get("residual_risk")
    if rr and _should_populate(rr):
        rr_content = _build_residual_risk_eval(project_id=project_id, profile=profile)
        document_crud.update_document(db, rr.id, DocumentUpdate(content=rr_content, status="draft"), project_id)
        stats.updated_documents.append("residual_risk")

    # 9b) Risk Acceptability Criteria (conservative template; no thresholds invented)
    rac = by_type.get("risk_acceptability_criteria")
    if rac and _should_populate(rac):
        rac_content = _draft_risk_acceptability_criteria(project_id=project_id, profile=profile, residual_risk_doc=rr)
        document_crud.update_document(db, rac.id, DocumentUpdate(content=rac_content, status="draft"), project_id)
        stats.updated_documents.append("risk_acceptability_criteria")

    # 9c) Benefit–Risk Analysis (structure only; no conclusions/decisions)
    bra = by_type.get("benefit_risk_analysis")
    if bra and _should_populate(bra):
        bra_content = _draft_benefit_risk_analysis(project_id=project_id, profile=profile, residual_risk_doc=rr)
        document_crud.update_document(db, bra.id, DocumentUpdate(content=bra_content, status="draft"), project_id)
        stats.updated_documents.append("benefit_risk_analysis")

    # 10) Traceability Matrix
    tm = by_type.get("traceability_matrix")
    if tm and _should_populate(tm):
        # Use the deterministic traceability builder to generate a gap-aware snapshot.
        from services.traceability_builder import build_traceability
        tm_content, _stats = build_traceability(db, project_id=project_id)
        document_crud.update_document(db, tm.id, DocumentUpdate(content=tm_content, status="draft"), project_id)
        stats.updated_documents.append("traceability_matrix")

    # 11) Risk Management Review (meeting-style template; auto-reference artifacts; no implied approval)
    rmr = by_type.get("risk_management_review")
    if rmr and _should_populate(rmr):
        refreshed = document_crud.get_documents_by_project(db, project_id)
        refreshed_by_type = {(d.type or "").lower(): d for d in refreshed}
        rmr_content = _draft_risk_management_review(
            project_id=project_id,
            profile=profile,
            artifacts={
                "rmp": refreshed_by_type.get("rmp"),
                "hazard_analysis": refreshed_by_type.get("hazard_analysis"),
                "fmea": refreshed_by_type.get("fmea"),
                "risk_controls_doc": refreshed_by_type.get("risk_controls_doc"),
                "residual_risk": refreshed_by_type.get("residual_risk"),
                "risk_acceptability_criteria": refreshed_by_type.get("risk_acceptability_criteria"),
                "benefit_risk_analysis": refreshed_by_type.get("benefit_risk_analysis"),
                "traceability_matrix": refreshed_by_type.get("traceability_matrix"),
            },
        )
        document_crud.update_document(db, rmr.id, DocumentUpdate(content=rmr_content, status="draft"), project_id)
        stats.updated_documents.append("risk_management_review")

    # 12) Post-Market & CAPA (structure-only scaffolds)
    # PMS Plan
    pms_plan = by_type.get("pms_plan")
    if pms_plan and _should_populate(pms_plan):
        risks_exist = False
        try:
            from crud import risk_item as _risk_item_crud
            risks_exist = len(_risk_item_crud.get_risk_items_by_project(db, project_id)) > 0
        except Exception:
            risks_exist = False
        pms_plan_content = _draft_pms_plan(
            project_id=project_id,
            profile=profile,
            components=components,
            refs={
                "hazard_analysis": _d("hazard_analysis"),
                "fmea": _d("fmea"),
                "risk_controls_doc": _d("risk_controls_doc"),
            },
            risks_exist=risks_exist,
        )
        document_crud.update_document(db, pms_plan.id, DocumentUpdate(content=pms_plan_content, status="draft"), project_id)
        stats.updated_documents.append("pms_plan")

    # PMS Report
    pms_report = by_type.get("pms_report")
    if pms_report and _should_populate(pms_report):
        pms_report_content = _draft_pms_report(
            project_id=project_id,
            profile=profile,
            refs={
                "pms_plan": _d("pms_plan"),
                "hazard_analysis": _d("hazard_analysis"),
                "fmea": _d("fmea"),
            },
        )
        document_crud.update_document(db, pms_report.id, DocumentUpdate(content=pms_report_content, status="draft"), project_id)
        stats.updated_documents.append("pms_report")

    # CAPA (CAPA log scaffold)
    capa_doc = by_type.get("capa")
    if capa_doc and _should_populate(capa_doc):
        capa_content = _draft_capa_log(project_id=project_id, profile=profile)
        document_crud.update_document(db, capa_doc.id, DocumentUpdate(content=capa_content, status="draft"), project_id)
        stats.updated_documents.append("capa")

    # 13) Usability & Human Factors (structure-only scaffolds)
    ura = by_type.get("usability_risk_analysis")
    if ura and _should_populate(ura):
        ura_content = _draft_usability_risk_analysis(
            project_id=project_id,
            profile=profile,
            components=components,
            refs={
                "hazard_analysis": _d("hazard_analysis"),
                "fmea": _d("fmea"),
                "risk_controls_doc": _d("risk_controls_doc"),
            },
        )
        document_crud.update_document(db, ura.id, DocumentUpdate(content=ura_content, status="draft"), project_id)
        stats.updated_documents.append("usability_risk_analysis")

    hf = by_type.get("hf_validation")
    if hf and _should_populate(hf):
        hf_content = _draft_hf_validation(project_id=project_id, profile=profile)
        document_crud.update_document(db, hf.id, DocumentUpdate(content=hf_content, status="draft"), project_id)
        stats.updated_documents.append("hf_validation")

    return stats.as_dict()


def build_project_setup_scaffolds(
    db: Session, *, project_id: str
) -> Dict[str, str]:
    """
    Pure helper (no side effects): build deterministic draft scaffolds from
    ProjectProfile + Components for comparison/tagging/upgrade flows.

    Note: This does NOT seed any DB rows (e.g., FMEA rows).
    """
    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)

    di_content, di_entries = _build_design_inputs(project_id=project_id, profile=profile, components=components)
    do_content, do_entries = _build_design_outputs(project_id=project_id, profile=profile, design_inputs=di_entries)
    vv_plan_content, vv_items = _build_vv_plan(db, project_id=project_id, profile=profile, design_inputs=di_entries)

    # FMEA content scaffold is based on whatever rows currently exist; no seeding.
    fmea_content = _draft_fmea_table(db, project_id=project_id, components=components)

    tm_content = _build_traceability_matrix(
        project_id=project_id,
        profile=profile,
        components=components,
        design_inputs=di_entries,
        design_outputs=do_entries,
        vv_items=vv_items,
        fmea_rows=fmea_crud.get_fmea_rows_by_project(db, project_id),
    )

    return {
        "rmp": _draft_rmp(project_id=project_id, profile=profile, components=components),
        "rmf": _draft_rmf_scaffold(project_id=project_id, profile=profile, components=components),
        "risk_acceptability_criteria": _draft_risk_acceptability_criteria(project_id=project_id, profile=profile, residual_risk_doc=None),
        "hazard_analysis": _draft_hazard_analysis(project_id=project_id, profile=profile, components=components),
        "benefit_risk_analysis": _draft_benefit_risk_analysis(project_id=project_id, profile=profile, residual_risk_doc=None),
        "fmea": fmea_content,
        "risk_management_review": _draft_risk_management_review(
            project_id=project_id,
            profile=profile,
            artifacts={},
        ),
        "design_dev_plan": _draft_design_dev_plan(project_id=project_id, profile=profile, components=components, refs={}),
        "design_reviews": _draft_design_reviews(project_id=project_id, profile=profile, refs={}),
        "design_change_record": _draft_design_change_record_base(project_id=project_id, profile=profile),
        "design_inputs_doc": di_content,
        "design_outputs_doc": do_content,
        "vv_plan": vv_plan_content,
        "vv_evidence": _build_vv_evidence_report(project_id=project_id, profile=profile, vv_items=vv_items),
        "validation_summary": _build_validation_summary(project_id=project_id, profile=profile, vv_evidence_doc=None, residual_risk_doc=None),
        "risk_controls_doc": _build_risk_controls_doc(db, project_id=project_id, profile=profile, components=components),
        "residual_risk": _build_residual_risk_eval(project_id=project_id, profile=profile),
        "traceability_matrix": tm_content,
        "pms_plan": _draft_pms_plan(project_id=project_id, profile=profile, components=components, refs={}, risks_exist=False),
        "pms_report": _draft_pms_report(project_id=project_id, profile=profile, refs={}),
        "capa": _draft_capa_log(project_id=project_id, profile=profile),
        "usability_risk_analysis": _draft_usability_risk_analysis(project_id=project_id, profile=profile, components=components, refs={}),
        "hf_validation": _draft_hf_validation(project_id=project_id, profile=profile),
    }

