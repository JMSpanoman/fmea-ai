"""
Default ISO-style 4x4 matrix (S1–S4 × P1–P4) and pacemaker-oriented special rules.

All hazard / device phrases live in JSON config (special_rules), not embedded in classification logic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def default_severity_scale() -> List[Dict[str, Any]]:
    return [
        {"level": 1, "code": "S1", "label": "No injury or negligible harm"},
        {"level": 2, "code": "S2", "label": "Reversible injury or temporary impairment"},
        {"level": 3, "code": "S3", "label": "Serious injury or permanent impairment"},
        {"level": 4, "code": "S4", "label": "Death or catastrophic harm"},
    ]


def default_probability_scale() -> List[Dict[str, Any]]:
    return [
        {"level": 1, "code": "P1", "label": "Remote"},
        {"level": 2, "code": "P2", "label": "Low"},
        {"level": 3, "code": "P3", "label": "Medium"},
        {"level": 4, "code": "P4", "label": "High"},
    ]


def default_detection_scale() -> List[Dict[str, Any]]:
    """Optional 1–10 FMEA-style detection scale; matrix path ignores detection unless hybrid/score."""
    return [{"level": i, "code": f"D{i}", "label": f"Detection level {i}"} for i in range(1, 11)]


def default_risk_matrix() -> Dict[str, Dict[str, str]]:
    """
    Rows = severity level 1..4, cols = probability level 1..4.
    Values: Acceptable | ALARP | Unacceptable
    """
    return {
        "1": {"1": "Acceptable", "2": "Acceptable", "3": "ALARP", "4": "ALARP"},
        "2": {"1": "Acceptable", "2": "ALARP", "3": "ALARP", "4": "Unacceptable"},
        "3": {"1": "ALARP", "2": "ALARP", "3": "Unacceptable", "4": "Unacceptable"},
        "4": {"1": "ALARP", "2": "Unacceptable", "3": "Unacceptable", "4": "Unacceptable"},
    }


def default_score_thresholds() -> Dict[str, Any]:
    """Secondary score bands when evaluation_method is score or hybrid (RPN = S×O×D)."""
    return {
        "acceptable_max_rpn": 24,
        "alarp_max_rpn": 120,
        # Optional explicit mapping from 1–10 FMEA inputs to 1–4 matrix indices
        "fmea_severity_to_matrix_index": {i: min(4, max(1, (i + 2) // 3)) for i in range(1, 11)},
        "fmea_occurrence_to_matrix_index": {i: min(4, max(1, (i + 2) // 3)) for i in range(1, 11)},
    }


def pacemaker_special_rules() -> Dict[str, Any]:
    """
    Keyword lists and declarative rules. Device / hazard wording is data-driven for auditability.
    """
    critical_function_keywords = [
        "loss of pacing",
        "incorrect pacing",
        "failure to pace",
        "battery depletion",
        "lead fracture",
        "lead failure",
        "sensing failure",
        "therapy delivery failure",
        "failure to sense",
        "oversensing",
        "undersensing",
    ]
    essential_function_keywords = [
        "loss of essential function",
        "loss of therapy",
        "no output",
        "device reset",
    ]
    # Implantable pacemaker — regulated critical hazard categories (text in row fields; matched case-insensitively).
    critical_hazard_category_keywords = [
        "loss of pacing",
        "incorrect pacing",
        "failure to deliver therapy",
        "therapy delivery failure",
        "failure to pace",
        "battery depletion",
        "lead failure",
        "lead dislodgement",
        "dislodgement",
        "sensing failure",
    ]
    return {
        "critical_function_keywords": critical_function_keywords,
        "essential_function_keywords": essential_function_keywords,
        "critical_hazard_category_keywords": critical_hazard_category_keywords,
        "device_context": {
            "implantable_pacemaker_profile": True,
            "life_sustaining": True,
        },
        # At least matrix band S4 (index 4) for matched hazards unless waived + documented; see docs.
        "critical_hazard_policies": {
            "enabled": True,
            "keyword_list_ref": "critical_hazard_category_keywords",
            "minimum_severity_matrix_index_floor": 4,
            "require_system_level_verification": True,
            "require_justification_when_not_eliminated": True,
        },
        # Thresholds are on the FMEA row numeric scales (not matrix band indices).
        # Adjust per project if your severity scale defines "death" at a different level.
        "mandatory_policies": {
            "enabled": True,
            "death_minimum_fmea_severity": 5,
            "residual_review_minimum_fmea_severity": 4,
            "release_review_disciplines": ["Engineering", "Clinical", "Quality"],
        },
        # Residual-only ISO 14971-style acceptability (after risk controls); omit key for same defaults.
        "residual_acceptability_policies": {
            "enabled": True,
            "acceptable_requires_documented_rationale": True,
            "alarp_requires_documented_justification": True,
            "alarp_requires_feasibility_attestations": True,
            "alarp_requires_formal_release_approval": True,
        },
        # Benefit–risk documentation + multi-party acceptance (omit lists to use code defaults).
        "benefit_risk_workflow_policy": {
            "enabled": True,
            "apply_when": "formal_bra_required",
            "use_multi_party_approval": True,
        },
        # Aggregate gate: line items + ProjectProfile attestations (see docs/RISK_RULE_ENGINE.md).
        "global_residual_acceptability_policy": {
            "enabled": True,
            "require_residual_classified": True,
            "require_unacceptable_escape_attestation": True,
            "require_no_row_release_blockers": True,
            "require_overall_benefit_risk_profile_attested": True,
            "require_rmr_overall_conclusion_attested": True,
        },
        "rules": [
            {
                "id": "s4_benefit_risk",
                "type": "benefit_risk_required",
                "condition": {"severity_matrix_gte": 4},
            },
            {
                "id": "serious_residual_justification",
                "type": "reviewer_justification_required",
                "condition": {"residual_severity_matrix_gte": 3},
            },
            {
                "id": "critical_function_escalation",
                "type": "min_classification",
                "condition": {"text_matches_any": "critical_function_keywords"},
                "value": "ALARP",
            },
            {
                "id": "critical_function_flag",
                "type": "set_critical_function_flag",
                "condition": {"text_matches_any": "critical_function_keywords"},
                "value": True,
            },
            {
                "id": "life_sustaining_essential_escalation",
                "type": "min_classification",
                "condition": {
                    "all": [
                        {"device_context_equals": {"life_sustaining": True}},
                        {"text_matches_any": "essential_function_keywords"},
                    ]
                },
                "value": "ALARP",
            },
        ],
    }


def build_default_criteria_payload(
    *,
    evaluation_method: str = "matrix",
    include_pacemaker_rules: bool = True,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "evaluation_method": evaluation_method,
        "severity_scale": default_severity_scale(),
        "probability_scale": default_probability_scale(),
        "detection_scale": default_detection_scale(),
        "risk_matrix": default_risk_matrix(),
        "score_thresholds": default_score_thresholds(),
        "special_rules": (
            pacemaker_special_rules()
            if include_pacemaker_rules
            else {"rules": [], "global_residual_acceptability_policy": {"enabled": False}}
        ),
    }
    return deepcopy(payload)
