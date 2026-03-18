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

# Source type for each section for audit transparency
SOURCE_APPROVED_PROJECT = "approved_project"
SOURCE_ORG_DEFAULT = "org_default"
SOURCE_SYSTEM_DRAFT = "system_draft"
SOURCE_AI_GENERATED = "ai_generated"
SOURCE_PLACEHOLDER = "placeholder"

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
            return override.decision_rules.strip(), SOURCE_APPROVED_PROJECT
        if org and org.decision_rules:
            return org.decision_rules.strip(), SOURCE_ORG_DEFAULT
        return SYSTEM_DECISION_RULES, SOURCE_SYSTEM_DRAFT

    severity_scale, src_sev = _get_severity()
    probability_scale, src_prob = _get_probability()
    risk_matrix, src_mat = _get_matrix()
    decision_rules, src_dr = _get_decision_rules()

    section_sources["severity_scale"] = src_sev
    section_sources["probability_scale"] = src_prob
    section_sources["risk_matrix"] = src_mat
    section_sources["decision_rules"] = src_dr

    return {
        "severity_scale": severity_scale,
        "probability_scale": probability_scale,
        "risk_matrix": risk_matrix,
        "decision_rules": decision_rules,
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
    trace = report.get("traceability_references") or {}
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
) -> Dict[str, Any]:
    """
    Build full Risk Acceptability Criteria report (all 19 sections).
    Returns structured dict with header, sections, source_metadata, manual_review_items.
    """
    merged, section_sources = get_merged_criteria(db, project_id)
    device_name = getattr(profile, "device_description", None) if profile else None
    intended_use = getattr(profile, "intended_use", None) if profile else None

    # Resolve traceability links (documents by type)
    from crud import document as document_crud
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = { (d.type or "").lower(): d for d in docs }
    traceability_links = {
        "risk_management_plan": {"id": getattr(by_type.get("rmp"), "id", None), "status": getattr(by_type.get("rmp"), "status", None)} if by_type.get("rmp") else {"id": None, "status": None},
        "hazard_analysis": {"id": getattr(by_type.get("hazard_analysis"), "id", None), "status": getattr(by_type.get("hazard_analysis"), "status", None)} if by_type.get("hazard_analysis") else {"id": None, "status": None},
        "residual_risk_evaluation": {"id": getattr(by_type.get("residual_risk"), "id", None), "status": getattr(by_type.get("residual_risk"), "status", None)} if by_type.get("residual_risk") else {"id": None, "status": None},
        "benefit_risk_analysis": {"id": getattr(by_type.get("benefit_risk_analysis"), "id", None), "status": getattr(by_type.get("benefit_risk_analysis"), "status", None)} if by_type.get("benefit_risk_analysis") else {"id": None, "status": None},
        "clinical_evaluation": {"id": getattr(by_type.get("clinical_evaluation"), "id", None), "status": getattr(by_type.get("clinical_evaluation"), "status", None)} if by_type.get("clinical_evaluation") else {"id": None, "status": None},
        "post_market_surveillance": {"id": getattr(by_type.get("pms_plan"), "id", None), "status": getattr(by_type.get("pms_plan"), "status", None)} if by_type.get("pms_plan") else {"id": None, "status": None},
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
            "source_type": SOURCE_PLACEHOLDER,
        },
        "purpose": {
            "text": "This document defines how risks are classified as acceptable, conditionally acceptable (ALARP), or unacceptable, and how those criteria are used during initial and residual risk evaluation in accordance with ISO 14971.",
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "scope": {
            "text": f"This criteria applies to the product(s) and hazard analyses for project: {project_name}. Scope covers all hazards identified in the risk management file and residual risk evaluations for this project. If exact product scope is not yet defined, update this section with the specific product or product family.",
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "regulatory_basis": {
            "text": "This document may support compliance with ISO 14971:2019 (Medical devices — Application of risk management). ISO/TR 24971 may be used as guidance. Applicable regulatory expectations (e.g. FDA, EU MDR) should be reviewed against applicable market requirements. No legal or regulatory claim is made; the organization is responsible for ensuring compliance.",
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "definitions": {
            "items": SYSTEM_DEFINITIONS,
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "severity_scale": {
            "scale": merged["severity_scale"],
            "source_type": section_sources.get("severity_scale", SOURCE_SYSTEM_DRAFT),
            "label": "Default draft values — replace with organization-approved scale if different.",
        },
        "probability_scale": {
            "scale": merged["probability_scale"],
            "source_type": section_sources.get("probability_scale", SOURCE_SYSTEM_DRAFT),
            "label": "Default draft values — replace with organization-approved scale if different.",
        },
        "risk_matrix": {
            "matrix": merged["risk_matrix"].get("matrix", merged["risk_matrix"]) if isinstance(merged["risk_matrix"], dict) else merged["risk_matrix"],
            "description": merged["risk_matrix"].get("description") if isinstance(merged["risk_matrix"], dict) else None,
            "source_type": section_sources.get("risk_matrix", SOURCE_SYSTEM_DRAFT),
            "label": "System-proposed draft matrix for team review. Do not use as official policy until approved." if section_sources.get("risk_matrix") == SOURCE_SYSTEM_DRAFT else None,
        },
        "decision_rules": {
            "text": merged["decision_rules"],
            "source_type": section_sources.get("decision_rules", SOURCE_SYSTEM_DRAFT),
        },
        "residual_risk_rules": {
            "text": SYSTEM_RESIDUAL_RISK_RULES,
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "benefit_risk_triggers": {
            "text": SYSTEM_BENEFIT_RISK_TRIGGERS,
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "control_effectiveness_expectations": {
            "text": "Risk controls shall be verified and, where applicable, validated. Examples: design verification, testing, inspection, software validation, labeling review, clinical evaluation support where applicable.",
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "overall_residual_risk": {
            "text": "Overall residual risk across the device shall be evaluated, not only individual risks. If data is unavailable, the review team shall complete this evaluation and document the conclusion.",
            "source_type": SOURCE_PLACEHOLDER,
            "requires_human_review": True,
        },
        "roles_and_responsibilities": {
            "roles": [
                {"role": "Risk Management Lead", "name": "To be assigned", "responsibility": "Owns risk management process and criteria."},
                {"role": "Engineering", "name": "To be assigned", "responsibility": "Implements risk controls and provides technical input."},
                {"role": "Clinical / Medical", "name": "To be assigned", "responsibility": "Clinical input and benefit-risk where applicable."},
                {"role": "Quality Assurance / Regulatory", "name": "To be assigned", "responsibility": "Ensures compliance and review."},
                {"role": "Approver", "name": "To be assigned", "responsibility": "Final approval of criteria and risk acceptability."},
            ],
            "source_type": SOURCE_PLACEHOLDER,
            "requires_human_review": True,
        },
        "review_and_approval": {
            "prepared_by": "To be assigned",
            "reviewed_by": "To be assigned",
            "approved_by": "To be assigned",
            "signature_date_placeholders": True,
            "version_history": [],
            "source_type": SOURCE_PLACEHOLDER,
            "requires_human_review": True,
        },
        "traceability_references": traceability_links,
        "ai_transparency": {
            "text": "Sections populated from project or organization configuration are deterministic. Sections marked 'system_draft' or 'placeholder' are system-proposed or require manual input. Any AI-assisted narrative is explicitly marked. All generated content requires human review and approval before use as approved criteria.",
            "source_type": SOURCE_SYSTEM_DRAFT,
        },
        "manual_review_items": [],
        "source_metadata": section_sources,
    }

    report["manual_review_items"] = detect_gaps(db, project_id, project_name, profile, section_sources, report)
    return report
