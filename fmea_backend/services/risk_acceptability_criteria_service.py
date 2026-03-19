"""
Risk Acceptability Criteria report generation (ISO 14971).
Three-tier precedence: project-approved → org default → system draft.
Deterministic generation; AI only for optional narrative in clearly marked sections.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from services.risk_acceptability_defaults import EDITABLE_DEFAULTS, DEFAULT_ALARP_TERMINOLOGY

# Source type for each section for audit transparency
SOURCE_APPROVED_PROJECT = "approved_project"
SOURCE_ORG_DEFAULT = "org_default"
SOURCE_SYSTEM_DRAFT = "system_draft"
SOURCE_AI_GENERATED = "ai_generated"
SOURCE_PLACEHOLDER = "placeholder"
SOURCE_SYSTEM_DEFAULT = "system_default"
SOURCE_USER_EDITED = "user_edited"
SOURCE_PROJECT_OVERRIDE = "project_override"

SECTION_KEYS = [
    "purpose",
    "scope",
    "regulatory_basis",
    "definitions",
    "severity_scale",
    "severity_rationale",
    "probability_scale",
    "probability_rationale",
    "alarp_terminology",
    "risk_matrix",
    "matrix_rationale",
    "decision_rule_wording",
    "decision_rules_rationale",
    "residual_risk_rules",
    "benefit_risk_triggers",
    "control_effectiveness",
    "overall_residual_risk",
    "roles_and_responsibilities",
    "traceability",
    "ai_transparency",
    "manual_review_items",
]

# System-proposed default values (always marked as draft for team review)
SYSTEM_SEVERITY_SCALE = [
    {"level": 1, "label": "Negligible", "definition": "No injury or negligible; no medical intervention."},
    {"level": 2, "label": "Minor", "definition": "Minor temporary injury; reversible; first aid or minimal intervention."},
    {"level": 3, "label": "Serious", "definition": "Serious injury or medical intervention required; may be reversible."},
    {"level": 4, "label": "Critical", "definition": "Life-threatening injury; permanent impairment; urgent intervention."},
    {"level": 5, "label": "Death", "definition": "Death or catastrophic harm."},
]

SYSTEM_PROBABILITY_SCALE = [
    {"level": 1, "label": "Remote", "definition": "Unlikely to occur", "frequency_text": None},
    {"level": 2, "label": "Low", "definition": "Possible but uncommon", "frequency_text": None},
    {"level": 3, "label": "Occasional", "definition": "Could occur occasionally", "frequency_text": None},
    {"level": 4, "label": "Probable", "definition": "Likely to occur", "frequency_text": None},
    {"level": 5, "label": "Frequent", "definition": "Expected to occur", "frequency_text": None},
]

# 5x5 matrix: severity (1-5) x probability (1-5) -> acceptability
SYSTEM_RISK_MATRIX = {
    "description": "System-proposed draft matrix for team review. Do not use as official policy until approved.",
    "rows": 5,
    "cols": 5,
    "matrix": [
        ["Acceptable", "Acceptable", "Acceptable", "ALARP", "ALARP"],
        ["Acceptable", "Acceptable", "ALARP", "ALARP", "Unacceptable"],
        ["Acceptable", "ALARP", "ALARP", "Unacceptable", "Unacceptable"],
        ["ALARP", "ALARP", "Unacceptable", "Unacceptable", "Unacceptable"],
        ["ALARP", "Unacceptable", "Unacceptable", "Unacceptable", "Unacceptable"],
    ],
    "source_type": SOURCE_SYSTEM_DRAFT,
}

SYSTEM_DECISION_RULES = """• Acceptable: No further risk reduction required unless easily implemented. Document rationale.
• ALARP / Conditionally acceptable: Requires documented justification and evaluation of additional feasible controls. Must be reviewed and approved.
• Unacceptable: Requires further mitigation or redesign before acceptance. Risk must be reduced or benefit-risk analysis performed."""

SYSTEM_RESIDUAL_RISK_RULES = """• Residual risk is evaluated after implementation of risk controls.
• When residual risk falls within "Acceptable" per the risk matrix, no further action is required beyond documentation.
• When residual risk remains in "ALARP", documented justification and review are required.
• When residual risk remains "Unacceptable", escalation to benefit-risk analysis is required before acceptance."""

SYSTEM_BENEFIT_RISK_TRIGGERS = """Formal benefit-risk analysis is required when:
• Residual risk remains high or unacceptable after implementation of feasible controls.
• Further risk reduction is not practicable without compromising device benefit.
• Device clinical benefit may justify remaining risk (to be documented and approved)."""

SYSTEM_DEFINITIONS = {
    "Risk": "Combination of the probability of occurrence of harm and the severity of that harm (ISO 14971).",
    "Severity": "Measure of the possible consequences of a hazard (ISO 14971).",
    "Probability of occurrence": "Likelihood of a hazardous situation occurring (ISO 14971).",
    "Risk acceptability": "Decision that residual risk is acceptable or unacceptable based on defined criteria.",
    "Residual risk": "Risk remaining after risk control measures have been implemented.",
    "Benefit-risk analysis": "Analysis in which the benefits of the intended use are compared to the overall residual risk.",
    "ALARP": "As Low As Reasonably Practicable; risk reduction as far as practicable without disproportionate burden.",
}


def get_project_override(db: Session, project_id: str) -> Optional[Any]:
    from models.risk_acceptability_criteria import ProjectRiskCriteriaOverride
    return (
        db.query(ProjectRiskCriteriaOverride)
        .filter(ProjectRiskCriteriaOverride.project_id == project_id)
        .order_by(ProjectRiskCriteriaOverride.updated_at.desc().nullslast())
        .first()
    )


def get_org_config(db: Session) -> Optional[Any]:
    from models.risk_acceptability_criteria import OrganizationRiskCriteriaConfig
    return (
        db.query(OrganizationRiskCriteriaConfig)
        .filter(OrganizationRiskCriteriaConfig.name == "default")
        .first()
    )


def get_rmp_criteria(db: Session, project_id: str) -> Optional[Dict[str, Any]]:
    from models.risk_management_plan import RiskManagementPlan
    rmp = (
        db.query(RiskManagementPlan)
        .filter(RiskManagementPlan.project_id == project_id, RiskManagementPlan.status == "approved")
        .order_by(RiskManagementPlan.updated_at.desc().nullslast())
        .first()
    )
    if not rmp or not rmp.acceptability_criteria_json:
        return None
    try:
        return json.loads(rmp.acceptability_criteria_json)
    except Exception:
        return None


def _parse_scale(j: Any) -> Optional[List[Dict]]:
    if j is None:
        return None
    if isinstance(j, list):
        return j
    if isinstance(j, dict):
        return [{"level": k, "label": v} if isinstance(v, str) else {"level": k, **v} for k, v in j.items()]
    return None


def get_merged_criteria(db: Session, project_id: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    Merge criteria from project override → org config → system draft.
    Returns (merged_criteria_dict, section_source_map).
    """
    section_sources: Dict[str, str] = {}
    override = get_project_override(db, project_id)
    org = get_org_config(db)
    rmp_criteria = get_rmp_criteria(db, project_id)

    def _get_severity() -> Tuple[List[Dict], str]:
        if override and override.severity_scale:
            try:
                scale = _parse_scale(override.severity_scale) if isinstance(override.severity_scale, str) else override.severity_scale
                if scale:
                    return scale, SOURCE_APPROVED_PROJECT
            except Exception:
                pass
        if org and org.severity_scale:
            try:
                scale = _parse_scale(org.severity_scale) if isinstance(org.severity_scale, str) else org.severity_scale
                if scale:
                    return scale, SOURCE_ORG_DEFAULT
            except Exception:
                pass
        if rmp_criteria and rmp_criteria.get("severity_scale"):
            s = rmp_criteria["severity_scale"]
            if isinstance(s, dict):
                scale = [{"level": k, "label": v} for k, v in s.items()]
            else:
                scale = s
            if scale:
                return scale, SOURCE_ORG_DEFAULT  # RMP as project-level
        return SYSTEM_SEVERITY_SCALE, SOURCE_SYSTEM_DRAFT

    def _get_probability() -> Tuple[List[Dict], str]:
        if override and override.probability_scale:
            try:
                scale = _parse_scale(override.probability_scale) if isinstance(override.probability_scale, str) else override.probability_scale
                if scale:
                    return scale, SOURCE_APPROVED_PROJECT
            except Exception:
                pass
        if org and org.probability_scale:
            try:
                scale = _parse_scale(org.probability_scale) if isinstance(org.probability_scale, str) else org.probability_scale
                if scale:
                    return scale, SOURCE_ORG_DEFAULT
            except Exception:
                pass
        if rmp_criteria and rmp_criteria.get("probability_scale"):
            s = rmp_criteria["probability_scale"]
            if isinstance(s, dict):
                scale = [{"level": k, "label": v} for k, v in s.items()]
            else:
                scale = s
            if scale:
                return scale, SOURCE_ORG_DEFAULT
        return SYSTEM_PROBABILITY_SCALE, SOURCE_SYSTEM_DRAFT

    def _get_matrix() -> Tuple[Dict, str]:
        if override and override.risk_matrix:
            try:
                m = override.risk_matrix if isinstance(override.risk_matrix, dict) else json.loads(override.risk_matrix)
                if m:
                    return m, SOURCE_APPROVED_PROJECT
            except Exception:
                pass
        if org and org.risk_matrix:
            try:
                m = org.risk_matrix if isinstance(org.risk_matrix, dict) else json.loads(org.risk_matrix)
                if m:
                    return m, SOURCE_ORG_DEFAULT
            except Exception:
                pass
        return SYSTEM_RISK_MATRIX, SOURCE_SYSTEM_DRAFT

    def _get_decision_rules() -> Tuple[str, str]:
        if override and override.decision_rules:
            return override.decision_rules.strip(), "project_override"
        if org and org.decision_rules:
            return org.decision_rules.strip(), SOURCE_ORG_DEFAULT
        return EDITABLE_DEFAULTS["decision_rule_wording"], SOURCE_SYSTEM_DEFAULT

    def _pick_text(field: str, default: Optional[str] = None) -> Tuple[Optional[str], str]:
        v = getattr(override, field, None) if override else None
        if v:
            return str(v), "project_override"
        v = getattr(org, field, None) if org else None
        if v:
            return str(v), SOURCE_ORG_DEFAULT
        return default, SOURCE_SYSTEM_DEFAULT

    def _pick_json(field: str, default: Any = None) -> Tuple[Any, str]:
        v = getattr(override, field, None) if override else None
        if v:
            if field == "terminology_overrides":
                return v, "project_override"
            return v, SOURCE_APPROVED_PROJECT
        v = getattr(org, field, None) if org else None
        if v:
            return v, SOURCE_ORG_DEFAULT
        return default, SOURCE_SYSTEM_DEFAULT

    severity_scale, src_sev = _get_severity()
    probability_scale, src_prob = _get_probability()
    risk_matrix, src_mat = _get_matrix()
    decision_rules, src_dr = _get_decision_rules()

    section_sources["severity_scale"] = src_sev
    section_sources["probability_scale"] = src_prob
    section_sources["risk_matrix"] = src_mat
    section_sources["decision_rules"] = src_dr

    terminology_overrides, src_terms = _pick_json("terminology_overrides", {"ALARP": EDITABLE_DEFAULTS["alarp_terminology"]})
    severity_rationale, src_sev_r = _pick_text("severity_rationale", EDITABLE_DEFAULTS["severity_rationale"])
    probability_rationale, src_prob_r = _pick_text("probability_rationale", EDITABLE_DEFAULTS["probability_rationale"])
    matrix_rationale, src_mat_r = _pick_text("matrix_rationale", EDITABLE_DEFAULTS["matrix_rationale"])
    decision_rationale, src_dec_r = _pick_text("decision_rules_rationale", EDITABLE_DEFAULTS["decision_rules_rationale"])
    methods, src_methods = _pick_json(
        "overall_residual_risk_methods",
        ["expert_panel_review", "aggregate_residual_risk_assessment", "benefit_risk_summary"],
    )
    approval_policy, src_policy = _pick_json("approval_policy", {"required_roles": ["risk_manager", "quality_lead", "approver"]})

    section_sources["terminology_overrides"] = src_terms
    section_sources["severity_rationale"] = src_sev_r
    section_sources["probability_rationale"] = src_prob_r
    section_sources["matrix_rationale"] = src_mat_r
    section_sources["decision_rules_rationale"] = src_dec_r
    section_sources["overall_residual_risk_methods"] = src_methods
    section_sources["approval_policy"] = src_policy

    return {
        "severity_scale": severity_scale,
        "probability_scale": probability_scale,
        "risk_matrix": risk_matrix,
        "decision_rules": decision_rules,
        "terminology_overrides": terminology_overrides or {},
        "severity_rationale": severity_rationale,
        "probability_rationale": probability_rationale,
        "matrix_rationale": matrix_rationale,
        "decision_rules_rationale": decision_rationale,
        "overall_residual_risk_methods": methods or [],
        "approval_policy": approval_policy or {},
    }, section_sources


def detect_gaps(
    db: Session,
    project_id: str,
    project_name: str,
    profile: Any,
    section_sources: Dict[str, str],
    report: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Identify missing inputs and required manual review items."""
    gaps: List[Dict[str, Any]] = []
    if section_sources.get("severity_scale") == SOURCE_SYSTEM_DRAFT:
        gaps.append({"id": "severity_scale", "message": "Approved severity scale not configured.", "section": "Severity scale"})
    if section_sources.get("probability_scale") == SOURCE_SYSTEM_DRAFT:
        gaps.append({"id": "probability_scale", "message": "Approved probability scale not configured.", "section": "Probability scale"})
    if section_sources.get("risk_matrix") == SOURCE_SYSTEM_DRAFT:
        gaps.append({"id": "risk_matrix", "message": "Official risk matrix not defined. Using system-proposed draft for team review.", "section": "Risk acceptability matrix"})
    if not (profile and getattr(profile, "device_description", None)):
        gaps.append({"id": "device_description", "message": "Device description not set in project profile.", "section": "Document header"})
    if not (profile and getattr(profile, "intended_use", None)):
        gaps.append({"id": "intended_use", "message": "Intended use not set in project profile.", "section": "Document header"})
    gaps.append({"id": "approver", "message": "Approver not assigned. Assign in Review and Approval section.", "section": "Review and approval"})
    # Optional: flag if key traceability documents are not yet linked
    trace_root = report.get("traceability_references") or {}
    trace = trace_root.get("items", trace_root) if isinstance(trace_root, dict) else {}
    res_risk_info = trace.get("residual_risk_evaluation", {}) if isinstance(trace, dict) else {}
    if not (res_risk_info.get("id") if isinstance(res_risk_info, dict) else None):
        gaps.append({"id": "residual_risk_doc", "message": "No linked Residual Risk Evaluation document. Link or create the document for full traceability.", "section": "Traceability references"})
    return gaps


def build_report(
    db: Session,
    project_id: str,
    project_name: str,
    profile: Any,
    generated_by: Optional[str] = None,
    include_ai_narrative: bool = False,
    existing_report: Optional[Dict[str, Any]] = None,
    regenerate_using_defaults: bool = False,
) -> Dict[str, Any]:
    """
    Build full Risk Acceptability Criteria report (all 19 sections).
    Returns structured dict with header, sections, source_metadata, manual_review_items.
    """
    merged, section_sources = get_merged_criteria(db, project_id)
    device_name = getattr(profile, "device_description", None) if profile else None
    intended_use = getattr(profile, "intended_use", None) if profile else None
    device_context_text = f"{device_name or ''} {intended_use or ''}".lower()
    high_criticality = any(k in device_context_text for k in ["implant", "life-sustaining", "life sustaining", "pacemaker"])

    # Resolve traceability links (documents by type)
    from crud import document as document_crud
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = { (d.type or "").lower(): d for d in docs }

    def _doc_ref(doc_type: str, key: str) -> Dict[str, Any]:
        d = by_type.get(doc_type)
        return {
            "id": getattr(d, "id", None) if d else None,
            "status": getattr(d, "status", None) if d else None,
            "last_updated_at": getattr(d, "updated_at", None).isoformat() if d and getattr(d, "updated_at", None) else None,
            "ui_link": f"/projects/{project_id}/documents/{getattr(d, 'id', '')}" if d else None,
            "key": key,
        }

    traceability_links = {
        "risk_management_plan": _doc_ref("rmp", "risk_management_plan"),
        "hazard_analysis": _doc_ref("hazard_analysis", "hazard_analysis"),
        "residual_risk_evaluation": _doc_ref("residual_risk", "residual_risk_evaluation"),
        "benefit_risk_analysis": _doc_ref("benefit_risk_analysis", "benefit_risk_analysis"),
        "clinical_evaluation": _doc_ref("clinical_evaluation", "clinical_evaluation"),
        "post_market_surveillance": _doc_ref("pms_plan", "post_market_surveillance"),
    }
    project_risk_context = _build_project_risk_context(db=db, project_id=project_id, docs=docs)

    now_iso = datetime.now(timezone.utc).isoformat()

    def _apply_alarp_terminology(text: str, selected_alarp: str) -> str:
        if not text:
            return text
        updated = text.replace("Acceptable with Justification (ALARP)", selected_alarp)
        updated = updated.replace("\"ALARP\"", f"\"{selected_alarp}\"")
        updated = updated.replace(" (ALARP)", f" ({selected_alarp})")
        return updated

    def _section_meta(
        source_type: str,
        *,
        value: Any = None,
        requires_human_review: bool = False,
        approved_by: Optional[str] = None,
        approved_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        completeness = "missing"
        if value is None:
            completeness = "missing"
        elif isinstance(value, str):
            completeness = "complete" if value.strip() else "missing"
        elif isinstance(value, (list, dict)):
            completeness = "complete" if len(value) > 0 else "partial"
        else:
            completeness = "complete"
        return {
            "source_type": source_type,
            "requires_human_review": requires_human_review,
            "completeness": completeness,
            "approved_by": approved_by,
            "approved_at": approved_at,
            "last_updated_at": now_iso,
        }

    report = {
        "document_header": {
            "document_title": "Risk Acceptability Criteria",
            "project_name": project_name,
            "project_id": project_id,
            "device_name": device_name or "Complete in project profile",
            "device_description": device_name or "Complete in project profile",
            "intended_use": intended_use or "Complete in project profile",
            "status": "draft",
            "version": 1,
            "date_generated": datetime.now(timezone.utc).isoformat(),
            "author_source": "SYSTEM-GENERATED DRAFT",
            "reviewer_placeholder": "To be assigned by project lead",
            "approver_placeholder": "To be assigned by project lead",
            **_section_meta(SOURCE_PLACEHOLDER, value=device_name or intended_use, requires_human_review=True),
        },
        "purpose": {
            "text": "This document defines how risks are classified as acceptable, conditionally acceptable (ALARP), or unacceptable, and how those criteria are used during initial and residual risk evaluation in accordance with ISO 14971.",
            **_section_meta(SOURCE_AI_GENERATED if include_ai_narrative else SOURCE_SYSTEM_DRAFT, value="x"),
        },
        "scope": {
            "text": (
                f"These criteria apply to the product(s) and hazard analyses for project: {project_name}. "
                "Scope covers all hazards identified in the risk management file and residual risk evaluations for this project. "
                "If exact product scope is not yet defined, update this section with the specific product or product family."
                f"{project_risk_context.get('scope_note', '')}"
            ),
            **_section_meta(SOURCE_AI_GENERATED if include_ai_narrative else SOURCE_SYSTEM_DRAFT, value="x"),
        },
        "regulatory_basis": {
            "text": "This document may support compliance with ISO 14971:2019 (Medical devices — Application of risk management). ISO/TR 24971 may be used as guidance. Applicable regulatory expectations (e.g. FDA, EU MDR) should be reviewed against applicable market requirements. No legal or regulatory claim is made; the organization is responsible for ensuring compliance.",
            **_section_meta(SOURCE_SYSTEM_DRAFT, value="x"),
        },
        "definitions": {
            "items": SYSTEM_DEFINITIONS,
            **_section_meta(SOURCE_SYSTEM_DRAFT, value=SYSTEM_DEFINITIONS),
        },
        "severity_scale": {
            "scale": merged["severity_scale"],
            "label": "Default draft values — replace with organization-approved scale if different.",
            "rationale": merged.get("severity_rationale"),
            **_section_meta(section_sources.get("severity_scale", SOURCE_SYSTEM_DRAFT), value=merged["severity_scale"], requires_human_review=section_sources.get("severity_scale") not in {"project_override", SOURCE_ORG_DEFAULT}),
        },
        "probability_scale": {
            "scale": merged["probability_scale"],
            "label": "Default draft values — replace with organization-approved scale if different.",
            "rationale": merged.get("probability_rationale"),
            **_section_meta(section_sources.get("probability_scale", SOURCE_SYSTEM_DRAFT), value=merged["probability_scale"], requires_human_review=section_sources.get("probability_scale") not in {"project_override", SOURCE_ORG_DEFAULT}),
        },
        "risk_matrix": {
            "matrix": merged["risk_matrix"].get("matrix", merged["risk_matrix"]) if isinstance(merged["risk_matrix"], dict) else merged["risk_matrix"],
            "description": (
                "System-proposed cautious draft for high-criticality device context. Requires formal project approval."
                if high_criticality and section_sources.get("risk_matrix") == SOURCE_SYSTEM_DRAFT
                else (merged["risk_matrix"].get("description") if isinstance(merged["risk_matrix"], dict) else None)
            ),
            "label": "System-proposed draft matrix for team review. Do not use as official policy until approved." if section_sources.get("risk_matrix") in {SOURCE_SYSTEM_DRAFT, SOURCE_SYSTEM_DEFAULT} else None,
            "rationale": merged.get("matrix_rationale"),
            **_section_meta(section_sources.get("risk_matrix", SOURCE_SYSTEM_DRAFT), value=merged["risk_matrix"], requires_human_review=section_sources.get("risk_matrix") not in {"project_override", SOURCE_ORG_DEFAULT}),
        },
        "decision_rules": {
            "text": (
                merged["decision_rules"] + "\n• For implantable/life-sustaining context, any residual high risk requires escalation and explicit approval."
                if high_criticality and section_sources.get("decision_rules") in {SOURCE_SYSTEM_DRAFT, SOURCE_SYSTEM_DEFAULT}
                else merged["decision_rules"]
            ),
            "rationale": merged.get("decision_rules_rationale"),
            **_section_meta(section_sources.get("decision_rules", SOURCE_SYSTEM_DRAFT), value=merged["decision_rules"], requires_human_review=section_sources.get("decision_rules") not in {"project_override", SOURCE_ORG_DEFAULT}),
        },
        "residual_risk_rules": {
            "text": SYSTEM_RESIDUAL_RISK_RULES,
            "methods": merged.get("overall_residual_risk_methods", []),
            **_section_meta(SOURCE_SYSTEM_DRAFT, value=SYSTEM_RESIDUAL_RISK_RULES),
        },
        "benefit_risk_triggers": {
            "text": f"{SYSTEM_BENEFIT_RISK_TRIGGERS}\n{project_risk_context.get('benefit_risk_note', '')}".strip(),
            **_section_meta(SOURCE_AI_GENERATED if include_ai_narrative else SOURCE_SYSTEM_DRAFT, value=SYSTEM_BENEFIT_RISK_TRIGGERS),
        },
        "control_effectiveness_expectations": {
            "text": "Risk controls shall be verified and, where applicable, validated. Examples: design verification, testing, inspection, software validation, labeling review, clinical evaluation support where applicable.",
            **_section_meta(SOURCE_SYSTEM_DRAFT, value="x"),
        },
        "overall_residual_risk": {
            "text": (
                "Overall residual risk across the device shall be evaluated, not only individual risks. "
                "If data is unavailable, the review team shall complete this evaluation and document the conclusion. "
                f"{project_risk_context.get('overall_residual_note', '')}"
            ).strip(),
            **_section_meta(SOURCE_PLACEHOLDER, value="x", requires_human_review=True),
        },
        "roles_and_responsibilities": {
            "roles": [
                {"role": "Risk Management Lead", "name": "To be assigned", "responsibility": "Owns risk management process and criteria."},
                {"role": "Engineering", "name": "To be assigned", "responsibility": "Implements risk controls and provides technical input."},
                {"role": "Clinical / Medical", "name": "To be assigned", "responsibility": "Clinical input and benefit-risk where applicable."},
                {"role": "Quality Assurance / Regulatory", "name": "To be assigned", "responsibility": "Ensures compliance and review."},
                {"role": "Approver", "name": "To be assigned", "responsibility": "Final approval of criteria and risk acceptability."},
            ],
            **_section_meta(SOURCE_PLACEHOLDER, value="x", requires_human_review=True),
        },
        "review_and_approval": {
            "prepared_by": "To be assigned",
            "reviewed_by": "To be assigned",
            "approved_by": "To be assigned",
            "signature_date_placeholders": True,
            "version_history": [],
            **_section_meta(SOURCE_PLACEHOLDER, value=[], requires_human_review=True),
        },
        "traceability_references": {
            "items": traceability_links,
            "project_context": project_risk_context.get("traceability_context", {}),
            "warnings": [],
            **_section_meta(SOURCE_SYSTEM_DRAFT, value=traceability_links),
        },
        "terminology": {
            "overrides": merged.get("terminology_overrides", {}),
            **_section_meta(section_sources.get("terminology_overrides", SOURCE_SYSTEM_DEFAULT), value=merged.get("terminology_overrides", {})),
        },
        "benefit_risk_workflow": {
            "trigger_reason": "Residual risk remains above acceptable threshold or further reduction not practicable.",
            "linked_evidence_inputs": [traceability_links.get("residual_risk_evaluation"), traceability_links.get("hazard_analysis")],
            "required_approvers": (merged.get("approval_policy") or {}).get("required_roles", ["risk_manager", "quality_lead", "approver"]),
            "decision_summary": "Pending formal benefit-risk decision when triggered.",
            "status": "pending",
            "linked_benefit_risk_document": traceability_links.get("benefit_risk_analysis"),
            **_section_meta(SOURCE_SYSTEM_DRAFT, value="x", requires_human_review=True),
        },
        "ai_transparency": {
            "text": "Sections populated from project or organization configuration are deterministic. Sections marked 'system_draft', 'system_default', or 'placeholder' are system-proposed, defaulted, or require manual input. Any AI-assisted narrative is explicitly marked. All generated content requires human review and approval before use as approved criteria.",
            **_section_meta(SOURCE_SYSTEM_DRAFT, value="x"),
        },
        "manual_review_items": [],
        "source_metadata": section_sources,
    }

    editable_defaults = {
        "decision_rule_wording": {
            "current_value": report["decision_rules"]["text"],
            "source_type": section_sources.get("decision_rules", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("decision_rules", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["decision_rule_wording"],
        },
        "alarp_terminology": {
            "current_value": (report.get("terminology", {}).get("overrides", {}) or {}).get("ALARP", EDITABLE_DEFAULTS["alarp_terminology"]),
            "source_type": section_sources.get("terminology_overrides", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("terminology_overrides", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["alarp_terminology"],
        },
        "severity_rationale": {
            "current_value": report["severity_scale"].get("rationale"),
            "source_type": section_sources.get("severity_rationale", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("severity_rationale", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["severity_rationale"],
        },
        "probability_rationale": {
            "current_value": report["probability_scale"].get("rationale"),
            "source_type": section_sources.get("probability_rationale", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("probability_rationale", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["probability_rationale"],
        },
        "matrix_rationale": {
            "current_value": report["risk_matrix"].get("rationale"),
            "source_type": section_sources.get("matrix_rationale", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("matrix_rationale", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["matrix_rationale"],
        },
        "decision_rules_rationale": {
            "current_value": report["decision_rules"].get("rationale"),
            "source_type": section_sources.get("decision_rules_rationale", SOURCE_SYSTEM_DEFAULT),
            "requires_human_review": section_sources.get("decision_rules_rationale", SOURCE_SYSTEM_DEFAULT) != "project_override",
            "last_edited_by": None,
            "last_edited_at": None,
            "default_value": EDITABLE_DEFAULTS["decision_rules_rationale"],
        },
    }

    # Preserve user edits by default across regeneration unless explicitly forced.
    if existing_report and not regenerate_using_defaults:
        existing_defaults = existing_report.get("editable_defaults", {})
        for key, value in existing_defaults.items():
            if isinstance(value, dict) and value.get("source_type") == SOURCE_USER_EDITED:
                editable_defaults[key] = value

    report["editable_defaults"] = editable_defaults
    selected_alarp = editable_defaults["alarp_terminology"]["current_value"] or DEFAULT_ALARP_TERMINOLOGY
    report["decision_rules"]["text"] = _apply_alarp_terminology(editable_defaults["decision_rule_wording"]["current_value"], selected_alarp)
    report["decision_rules"]["rationale"] = _apply_alarp_terminology(editable_defaults["decision_rules_rationale"]["current_value"], selected_alarp)
    report["severity_scale"]["rationale"] = editable_defaults["severity_rationale"]["current_value"]
    report["probability_scale"]["rationale"] = editable_defaults["probability_rationale"]["current_value"]
    report["risk_matrix"]["rationale"] = _apply_alarp_terminology(editable_defaults["matrix_rationale"]["current_value"], selected_alarp)
    report["terminology"]["overrides"] = {"ALARP": selected_alarp}
    report["residual_risk_rules"]["text"] = (
        "• Residual risk is evaluated after implementation of risk controls.\n"
        "• When residual risk falls within \"Acceptable\" per the risk matrix, no further action is required beyond documentation.\n"
        f"• When residual risk remains in \"{selected_alarp}\", documented justification and review are required.\n"
        "• When residual risk remains \"Unacceptable\", escalation to benefit-risk analysis is required before acceptance."
    )
    report["severity_rationale"] = {
        "text": report["severity_scale"]["rationale"],
        **_section_meta(editable_defaults["severity_rationale"]["source_type"], value=report["severity_scale"]["rationale"], requires_human_review=editable_defaults["severity_rationale"].get("requires_human_review", True)),
    }
    report["probability_rationale"] = {
        "text": report["probability_scale"]["rationale"],
        **_section_meta(editable_defaults["probability_rationale"]["source_type"], value=report["probability_scale"]["rationale"], requires_human_review=editable_defaults["probability_rationale"].get("requires_human_review", True)),
    }
    report["alarp_terminology"] = {
        "text": selected_alarp,
        **_section_meta(editable_defaults["alarp_terminology"]["source_type"], value=selected_alarp, requires_human_review=editable_defaults["alarp_terminology"].get("requires_human_review", True)),
    }
    report["matrix_rationale"] = {
        "text": report["risk_matrix"]["rationale"],
        **_section_meta(editable_defaults["matrix_rationale"]["source_type"], value=report["risk_matrix"]["rationale"], requires_human_review=editable_defaults["matrix_rationale"].get("requires_human_review", True)),
    }
    report["decision_rule_wording"] = {
        "text": report["decision_rules"]["text"],
        **_section_meta(editable_defaults["decision_rule_wording"]["source_type"], value=report["decision_rules"]["text"], requires_human_review=editable_defaults["decision_rule_wording"].get("requires_human_review", True)),
    }
    report["decision_rules_rationale"] = {
        "text": report["decision_rules"]["rationale"],
        **_section_meta(editable_defaults["decision_rules_rationale"]["source_type"], value=report["decision_rules"]["rationale"], requires_human_review=editable_defaults["decision_rules_rationale"].get("requires_human_review", True)),
    }

    # Traceability validation warnings
    t_warnings: List[str] = []
    for k, info in traceability_links.items():
        if not info.get("id"):
            t_warnings.append(f"{k.replace('_', ' ').title()} is not linked.")
        elif info.get("status") in {"draft", "in_review"}:
            t_warnings.append(f"{k.replace('_', ' ').title()} is not approved (status: {info.get('status')}).")
    report["traceability_references"]["warnings"] = t_warnings

    report["manual_review_items"] = detect_gaps(db, project_id, project_name, profile, section_sources, report)

    # Smarter gap structure
    enriched_manual = []
    for g in report["manual_review_items"]:
        gid = g.get("id")
        enriched_manual.append({
            "id": gid,
            "issue": g.get("message"),
            "why_it_matters": "This affects objective evidence and approval readiness for ISO 14971 audits.",
            "where_to_fix": g.get("section"),
            "effect_on_approval_readiness": "Blocks approval until resolved" if gid in {"severity_scale", "probability_scale", "risk_matrix", "approver"} else "Review required",
            "section": g.get("section"),
            "message": g.get("message"),
        })
    report["manual_review_items"] = enriched_manual
    report["manual_review_items"].append({
        "id": "alarp_terminology_review",
        "issue": "ALARP terminology: Confirm whether project or organization prefers “ALARP” or alternate terminology such as “Acceptable with Justification”.",
        "why_it_matters": "Terminology consistency affects risk classification interpretation and audit traceability.",
        "where_to_fix": "ALARP terminology",
        "effect_on_approval_readiness": "Review required",
        "section": "ALARP terminology",
        "message": "ALARP terminology: Confirm whether project or organization prefers “ALARP” or alternate terminology such as “Acceptable with Justification”.",
    })

    # Completeness/readiness scoring
    section_keys = [
        "purpose", "scope", "regulatory_basis", "definitions", "severity_scale", "probability_scale",
        "severity_rationale", "probability_rationale", "alarp_terminology", "risk_matrix", "matrix_rationale", "decision_rules", "decision_rule_wording", "decision_rules_rationale", "residual_risk_rules", "benefit_risk_triggers",
        "control_effectiveness_expectations", "overall_residual_risk", "roles_and_responsibilities",
        "review_and_approval", "traceability_references", "ai_transparency",
    ]
    complete = 0
    approved = 0
    requires_review = 0
    for sk in section_keys:
        s = report.get(sk, {})
        if isinstance(s, dict):
            if s.get("completeness") == "complete":
                complete += 1
            if s.get("source_type") == SOURCE_APPROVED_PROJECT:
                approved += 1
            if s.get("requires_human_review"):
                requires_review += 1
    blocked = [i["issue"] for i in report["manual_review_items"] if i.get("effect_on_approval_readiness", "").lower().startswith("blocks")]
    total = max(len(section_keys), 1)
    report["readiness"] = {
        "completeness_percentage": round((complete / total) * 100),
        "approved_content_percentage": round((approved / total) * 100),
        "sections_requiring_manual_review": requires_review,
        "blocked_approval_reasons": blocked,
    }
    report["section_metadata"] = {
        k: {
            "source_type": (report.get(k) or {}).get("source_type"),
            "requires_human_review": (report.get(k) or {}).get("requires_human_review", False),
            "completeness": (report.get(k) or {}).get("completeness", "missing"),
            "approved_by": (report.get(k) or {}).get("approved_by"),
            "approved_at": (report.get(k) or {}).get("approved_at"),
            "last_updated_at": (report.get(k) or {}).get("last_updated_at"),
        }
        for k in section_keys
    }
    generated_sections = _extract_sections_from_report(report)
    if existing_report and not regenerate_using_defaults:
        generated_sections = _merge_with_existing_sections(
            generated_sections,
            (existing_report or {}).get("sections") or {},
        )
    report["sections"] = generated_sections
    report["document_header"]["section_document_version"] = int((existing_report or {}).get("document_header", {}).get("section_document_version", 0) or 0) + 1
    _apply_sections_to_report(report, report["sections"])
    return report


def _mk_section(
    key: str,
    value: Any,
    source_type: str,
    *,
    approved: bool = False,
    is_user_edited: bool = False,
    version: int = 1,
    last_edited_by: Optional[str] = None,
    last_edited_at: Optional[str] = None,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "key": key,
        "value": value,
        "source_type": _normalize_source_type(source_type),
        "is_user_edited": is_user_edited,
        "approved": approved,
        "version": version,
        "last_edited_by": last_edited_by,
        "last_edited_at": last_edited_at,
        "history": history or [],
    }


def _extract_sections_from_report(report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    def _src(k: str, fallback: str = SOURCE_SYSTEM_DEFAULT) -> str:
        sec = report.get(k, {}) if isinstance(report.get(k), dict) else {}
        return sec.get("source_type") or (report.get("source_metadata", {}) or {}).get(k, fallback)

    definitions = (report.get("definitions", {}) or {}).get("items", {})
    severity = report.get("severity_scale", {}) or {}
    probability = report.get("probability_scale", {}) or {}
    matrix = report.get("risk_matrix", {}) or {}
    section_map = {
        "purpose": _mk_section("purpose", (report.get("purpose", {}) or {}).get("text", ""), _src("purpose", SOURCE_SYSTEM_DRAFT)),
        "scope": _mk_section("scope", (report.get("scope", {}) or {}).get("text", ""), _src("scope", SOURCE_SYSTEM_DRAFT)),
        "regulatory_basis": _mk_section("regulatory_basis", (report.get("regulatory_basis", {}) or {}).get("text", ""), _src("regulatory_basis", SOURCE_SYSTEM_DRAFT)),
        "definitions": _mk_section("definitions", definitions, _src("definitions", SOURCE_SYSTEM_DRAFT)),
        "severity_scale": _mk_section("severity_scale", severity.get("scale", []), _src("severity_scale", SOURCE_SYSTEM_DRAFT)),
        "severity_rationale": _mk_section("severity_rationale", (report.get("severity_rationale", {}) or {}).get("text", severity.get("rationale", "")), _src("severity_rationale", SOURCE_SYSTEM_DEFAULT)),
        "probability_scale": _mk_section("probability_scale", probability.get("scale", []), _src("probability_scale", SOURCE_SYSTEM_DRAFT)),
        "probability_rationale": _mk_section("probability_rationale", (report.get("probability_rationale", {}) or {}).get("text", probability.get("rationale", "")), _src("probability_rationale", SOURCE_SYSTEM_DEFAULT)),
        "alarp_terminology": _mk_section("alarp_terminology", (report.get("alarp_terminology", {}) or {}).get("text", ((report.get("terminology", {}) or {}).get("overrides", {}) or {}).get("ALARP", DEFAULT_ALARP_TERMINOLOGY)), _src("alarp_terminology", SOURCE_SYSTEM_DEFAULT)),
        "risk_matrix": _mk_section("risk_matrix", matrix.get("matrix", []), _src("risk_matrix", SOURCE_SYSTEM_DRAFT)),
        "matrix_rationale": _mk_section("matrix_rationale", (report.get("matrix_rationale", {}) or {}).get("text", matrix.get("rationale", "")), _src("matrix_rationale", SOURCE_SYSTEM_DEFAULT)),
        "decision_rule_wording": _mk_section("decision_rule_wording", (report.get("decision_rule_wording", {}) or {}).get("text", (report.get("decision_rules", {}) or {}).get("text", "")), _src("decision_rule_wording", SOURCE_SYSTEM_DEFAULT)),
        "decision_rules_rationale": _mk_section("decision_rules_rationale", (report.get("decision_rules_rationale", {}) or {}).get("text", (report.get("decision_rules", {}) or {}).get("rationale", "")), _src("decision_rules_rationale", SOURCE_SYSTEM_DEFAULT)),
        "residual_risk_rules": _mk_section("residual_risk_rules", (report.get("residual_risk_rules", {}) or {}).get("text", ""), _src("residual_risk_rules", SOURCE_SYSTEM_DRAFT)),
        "benefit_risk_triggers": _mk_section("benefit_risk_triggers", (report.get("benefit_risk_triggers", {}) or {}).get("text", ""), _src("benefit_risk_triggers", SOURCE_SYSTEM_DRAFT)),
        "control_effectiveness": _mk_section("control_effectiveness", (report.get("control_effectiveness_expectations", {}) or {}).get("text", ""), _src("control_effectiveness_expectations", SOURCE_SYSTEM_DRAFT)),
        "overall_residual_risk": _mk_section("overall_residual_risk", (report.get("overall_residual_risk", {}) or {}).get("text", ""), _src("overall_residual_risk", SOURCE_PLACEHOLDER)),
        "roles_and_responsibilities": _mk_section("roles_and_responsibilities", (report.get("roles_and_responsibilities", {}) or {}).get("roles", []), _src("roles_and_responsibilities", SOURCE_PLACEHOLDER)),
        "traceability": _mk_section("traceability", (report.get("traceability_references", {}) or {}).get("items", {}), _src("traceability_references", SOURCE_SYSTEM_DRAFT)),
        "ai_transparency": _mk_section("ai_transparency", (report.get("ai_transparency", {}) or {}).get("text", ""), _src("ai_transparency", SOURCE_SYSTEM_DRAFT)),
        "manual_review_items": _mk_section("manual_review_items", report.get("manual_review_items", []), _src("manual_review_items", SOURCE_SYSTEM_DRAFT)),
    }
    return section_map


def _merge_with_existing_sections(
    generated_sections: Dict[str, Dict[str, Any]],
    existing_sections: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = dict(generated_sections)
    for key, existing in (existing_sections or {}).items():
        if key not in merged:
            continue
        if not isinstance(existing, dict):
            continue
        if existing.get("is_user_edited") or existing.get("approved"):
            existing["source_type"] = _normalize_source_type(existing.get("source_type"))
            merged[key] = existing
            continue
        merged[key]["source_type"] = _normalize_source_type(merged[key].get("source_type"))
        merged[key]["version"] = int(existing.get("version", 1) or 1)
        merged[key]["history"] = existing.get("history", []) or []
    return merged


def _apply_sections_to_report(report: Dict[str, Any], sections: Dict[str, Dict[str, Any]]) -> None:
    if not isinstance(sections, dict):
        return
    if "purpose" in sections:
        report.setdefault("purpose", {})["text"] = sections["purpose"].get("value", "")
        report["purpose"]["source_type"] = _normalize_source_type(sections["purpose"].get("source_type"))
    if "scope" in sections:
        report.setdefault("scope", {})["text"] = sections["scope"].get("value", "")
        report["scope"]["source_type"] = _normalize_source_type(sections["scope"].get("source_type"))
    if "regulatory_basis" in sections:
        report.setdefault("regulatory_basis", {})["text"] = sections["regulatory_basis"].get("value", "")
        report["regulatory_basis"]["source_type"] = _normalize_source_type(sections["regulatory_basis"].get("source_type"))
    if "definitions" in sections:
        report.setdefault("definitions", {})["items"] = sections["definitions"].get("value", {})
        report["definitions"]["source_type"] = _normalize_source_type(sections["definitions"].get("source_type"))
    if "severity_scale" in sections:
        report.setdefault("severity_scale", {})["scale"] = sections["severity_scale"].get("value", [])
        report["severity_scale"]["source_type"] = _normalize_source_type(sections["severity_scale"].get("source_type"))
    if "severity_rationale" in sections:
        sev_val = sections["severity_rationale"].get("value", "")
        report.setdefault("severity_scale", {})["rationale"] = sev_val
        report["severity_rationale"] = {"text": sev_val, "source_type": _normalize_source_type(sections["severity_rationale"].get("source_type"))}
    if "probability_scale" in sections:
        report.setdefault("probability_scale", {})["scale"] = sections["probability_scale"].get("value", [])
        report["probability_scale"]["source_type"] = _normalize_source_type(sections["probability_scale"].get("source_type"))
    if "probability_rationale" in sections:
        pr_val = sections["probability_rationale"].get("value", "")
        report.setdefault("probability_scale", {})["rationale"] = pr_val
        report["probability_rationale"] = {"text": pr_val, "source_type": _normalize_source_type(sections["probability_rationale"].get("source_type"))}
    if "alarp_terminology" in sections:
        alarp = sections["alarp_terminology"].get("value", DEFAULT_ALARP_TERMINOLOGY)
        report.setdefault("terminology", {})["overrides"] = {"ALARP": alarp}
        report["alarp_terminology"] = {"text": alarp, "source_type": _normalize_source_type(sections["alarp_terminology"].get("source_type"))}
    if "risk_matrix" in sections:
        report.setdefault("risk_matrix", {})["matrix"] = sections["risk_matrix"].get("value", [])
        report["risk_matrix"]["source_type"] = _normalize_source_type(sections["risk_matrix"].get("source_type"))
    if "matrix_rationale" in sections:
        m_val = sections["matrix_rationale"].get("value", "")
        report.setdefault("risk_matrix", {})["rationale"] = m_val
        report["matrix_rationale"] = {"text": m_val, "source_type": _normalize_source_type(sections["matrix_rationale"].get("source_type"))}
    if "decision_rule_wording" in sections:
        d_val = sections["decision_rule_wording"].get("value", "")
        report.setdefault("decision_rules", {})["text"] = d_val
        report["decision_rule_wording"] = {"text": d_val, "source_type": _normalize_source_type(sections["decision_rule_wording"].get("source_type"))}
    if "decision_rules_rationale" in sections:
        dr_val = sections["decision_rules_rationale"].get("value", "")
        report.setdefault("decision_rules", {})["rationale"] = dr_val
        report["decision_rules_rationale"] = {"text": dr_val, "source_type": _normalize_source_type(sections["decision_rules_rationale"].get("source_type"))}
    if "residual_risk_rules" in sections:
        report.setdefault("residual_risk_rules", {})["text"] = sections["residual_risk_rules"].get("value", "")
        report["residual_risk_rules"]["source_type"] = _normalize_source_type(sections["residual_risk_rules"].get("source_type"))
    if "benefit_risk_triggers" in sections:
        report.setdefault("benefit_risk_triggers", {})["text"] = sections["benefit_risk_triggers"].get("value", "")
        report["benefit_risk_triggers"]["source_type"] = _normalize_source_type(sections["benefit_risk_triggers"].get("source_type"))
    if "control_effectiveness" in sections:
        report.setdefault("control_effectiveness_expectations", {})["text"] = sections["control_effectiveness"].get("value", "")
        report["control_effectiveness_expectations"]["source_type"] = _normalize_source_type(sections["control_effectiveness"].get("source_type"))
    if "overall_residual_risk" in sections:
        report.setdefault("overall_residual_risk", {})["text"] = sections["overall_residual_risk"].get("value", "")
        report["overall_residual_risk"]["source_type"] = _normalize_source_type(sections["overall_residual_risk"].get("source_type"))
    if "roles_and_responsibilities" in sections:
        report.setdefault("roles_and_responsibilities", {})["roles"] = sections["roles_and_responsibilities"].get("value", [])
        report["roles_and_responsibilities"]["source_type"] = _normalize_source_type(sections["roles_and_responsibilities"].get("source_type"))
    if "traceability" in sections:
        report.setdefault("traceability_references", {})["items"] = sections["traceability"].get("value", {})
        report["traceability_references"]["source_type"] = _normalize_source_type(sections["traceability"].get("source_type"))
    if "ai_transparency" in sections:
        report.setdefault("ai_transparency", {})["text"] = sections["ai_transparency"].get("value", "")
        report["ai_transparency"]["source_type"] = _normalize_source_type(sections["ai_transparency"].get("source_type"))
    if "manual_review_items" in sections:
        report["manual_review_items"] = sections["manual_review_items"].get("value", [])


def _normalize_source_type(source_type: Any) -> str:
    raw = str(source_type or "").strip().lower()
    if raw in {SOURCE_SYSTEM_DEFAULT, SOURCE_ORG_DEFAULT, SOURCE_PROJECT_OVERRIDE, SOURCE_USER_EDITED}:
        return raw
    if raw in {"approved_project", "project_approved"}:
        return SOURCE_PROJECT_OVERRIDE
    if raw in {"system_draft", "placeholder", "ai_generated", SOURCE_PLACEHOLDER}:
        return SOURCE_SYSTEM_DEFAULT
    return SOURCE_SYSTEM_DEFAULT


def _build_project_risk_context(db: Session, project_id: str, docs: List[Any]) -> Dict[str, Any]:
    context: Dict[str, Any] = {}
    by_type = {(d.type or "").lower(): d for d in docs}

    def _snippet(doc_type: str, max_chars: int = 280) -> str:
        d = by_type.get(doc_type)
        if not d or not getattr(d, "content", None):
            return ""
        text = " ".join(str(d.content).split())
        return text[:max_chars]

    context["traceability_context"] = {
        "rmp_excerpt": _snippet("rmp"),
        "hazard_analysis_excerpt": _snippet("hazard_analysis"),
        "residual_risk_excerpt": _snippet("residual_risk"),
        "benefit_risk_excerpt": _snippet("benefit_risk_analysis"),
    }

    try:
        from models.hazard_analysis_item import HazardAnalysisItem
        hazard_count = (
            db.query(HazardAnalysisItem)
            .filter(HazardAnalysisItem.project_id == project_id)
            .count()
        )
    except Exception:
        hazard_count = 0

    try:
        from models.project_risk_item import ProjectRiskItem
        from models.device import Device
        risk_rows = (
            db.query(ProjectRiskItem)
            .join(Device, ProjectRiskItem.device_id == Device.id)
            .filter(Device.project_id == project_id)
            .all()
        )
        residual_summary: Dict[str, int] = {}
        for r in risk_rows:
            key = (getattr(r, "residual_risk_acceptability", None) or "unknown").strip().lower()
            residual_summary[key] = residual_summary.get(key, 0) + 1
    except Exception:
        residual_summary = {}

    context["scope_note"] = (
        f" Current project evidence: {hazard_count} hazard analysis row(s) captured."
        if hazard_count
        else ""
    )
    context["overall_residual_note"] = (
        f" Current residual risk classification counts: {residual_summary}."
        if residual_summary
        else ""
    )
    br_excerpt = context["traceability_context"].get("benefit_risk_excerpt")
    context["benefit_risk_note"] = (
        f" Project benefit-risk analysis reference excerpt: {br_excerpt}"
        if br_excerpt
        else ""
    )
    return context
