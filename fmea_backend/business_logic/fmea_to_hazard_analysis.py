"""
Map FMEA rows to hazard analysis item shape (for prefilling and report).
Used to transform FMEA data into hazard-analysis draft content without overwriting approved HA items.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional


def fmea_row_to_hazard_analysis_dict(
    fmea_row: Any,
    *,
    component_name: Optional[str] = None,
    risk_key: Optional[str] = None,
    project_id: Optional[str] = None,
    component_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert one FMEA row (ORM or dict) to a hazard-analysis item shape.
    Used for prefilling new HazardAnalysisItem or for report when no HA items exist.
    """
    def _get(obj: Any, key: str, default: Any = None) -> Any:
        if hasattr(obj, "get") and callable(obj.get):
            return obj.get(key, default)
        return getattr(obj, key, default) if obj is not None else default

    severity = _get(fmea_row, "severity")
    prob = _get(fmea_row, "probability")
    rpn = _get(fmea_row, "rpn")
    if severity is not None and prob is not None:
        try:
            s, p = int(severity), int(prob)
            if s * p >= 64:
                risk_level = "Critical"
            elif s * p >= 20:
                risk_level = "High"
            elif s * p >= 8:
                risk_level = "Medium"
            else:
                risk_level = "Low"
        except (TypeError, ValueError):
            risk_level = "Medium"
    else:
        risk_level = "Medium"

    res_sev = _get(fmea_row, "residual_severity")
    res_prob = _get(fmea_row, "residual_probability")
    res_rpn = _get(fmea_row, "residual_rpn")
    if res_sev is not None and res_prob is not None:
        try:
            s, p = int(res_sev), int(res_prob)
            if s * p >= 64:
                res_level = "Critical"
            elif s * p >= 20:
                res_level = "High"
            elif s * p >= 8:
                res_level = "Medium"
            else:
                res_level = "Low"
        except (TypeError, ValueError):
            res_level = "Low"
    else:
        res_level = "Low"

    mitigation = _get(fmea_row, "mitigation") or ""
    controls = [s.strip() for s in str(mitigation).split(";") if s.strip()] if mitigation else []
    if not controls and mitigation:
        controls = [str(mitigation)]

    return {
        "project_id": project_id,
        "component_id": component_id,
        "component_name": component_name,
        "risk_key": risk_key,
        "version_no": 1,
        "hazard_category": "Technical",
        "hazard": _get(fmea_row, "failure_mode") or "Malfunction or failure affecting safety",
        "foreseeable_sequence_of_events": _get(fmea_row, "cause") or "Cause to be documented; leads to failure mode and possible harm.",
        "hazardous_situation": "Device user or patient is exposed to the failure effect during use.",
        "harm": _get(fmea_row, "effect") or "Adverse outcome consistent with failure effect (to be specified).",
        "affected_user": "Patient",
        "failure_mode": _get(fmea_row, "failure_mode"),
        "cause_of_failure": _get(fmea_row, "cause"),
        "clinical_effect": _get(fmea_row, "effect"),
        "operating_mode": "Normal operation",
        "use_environment": None,
        "initial_severity": int(severity) if severity is not None else None,
        "initial_probability": int(prob) if prob is not None else None,
        "initial_risk_level": risk_level,
        "risk_control_measures": controls,
        "risk_control_type": ["inherent_safety_by_design", "protective_measures", "information_for_safety"][: min(len(controls), 3)],
        "control_implementation_notes": None,
        "residual_severity": int(res_sev) if res_sev is not None else None,
        "residual_probability": int(res_prob) if res_prob is not None else None,
        "residual_risk_level": res_level,
        "residual_risk_acceptability": "acceptable" if res_level in ("Low", "Medium") else "acceptable_with_justification",
        "related_design_input": [],
        "related_design_output": [],
        "verification_reference": [],
        "validation_reference": [],
        "requirement_ids": [],
        "approval_status": "draft",
        "reviewer_comments": None,
        "ai_generated": False,
        "ai_confidence": None,
        "source_context": "FMEA",
        "assumptions": ["Prefilled from FMEA; review and complete for hazard analysis."],
    }


def risk_item_version_to_hazard_analysis_dict(
    version: Any,
    risk_item: Any,
    *,
    component_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert risk_item_version + risk_item to hazard-analysis row shape (for report fallback).
    """
    def _get(obj: Any, key: str, default: Any = None) -> Any:
        if hasattr(obj, "get") and callable(obj.get):
            return obj.get(key, default)
        return getattr(obj, key, default) if obj is not None else default

    sev = _get(version, "severity")
    prob = _get(version, "probability_of_harm") or _get(version, "probability")
    level = _get(version, "risk_level") or "Medium"
    res_level = _get(version, "residual_risk_level") or "Low"
    controls = []
    for k in ("inherent_safety", "protective_measures", "information_for_safety", "control_measures_summary"):
        v = _get(version, k)
        if v and str(v).strip():
            controls.append(str(v).strip())
    if not controls and _get(version, "control_measures_summary"):
        controls = [str(_get(version, "control_measures_summary"))]

    return {
        "risk_item_id": _get(risk_item, "id"),
        "risk_item_version_id": _get(version, "id"),
        "component_name": component_name,
        "risk_key": _get(risk_item, "risk_key"),
        "version_no": _get(version, "version_number") or 1,
        "hazard_category": None,
        "hazard": _get(version, "hazard"),
        "foreseeable_sequence_of_events": _get(version, "sequence_of_events"),
        "hazardous_situation": _get(version, "hazardous_situation"),
        "harm": _get(version, "harm"),
        "affected_user": None,
        "failure_mode": _get(version, "failure_mode"),
        "cause_of_failure": None,
        "clinical_effect": _get(version, "harm"),
        "operating_mode": None,
        "use_environment": None,
        "initial_severity": int(sev) if sev is not None else None,
        "initial_probability": int(prob) if prob is not None else None,
        "initial_risk_level": level,
        "risk_control_measures": controls if controls else None,
        "risk_control_type": None,
        "control_implementation_notes": None,
        "residual_severity": _get(version, "residual_severity"),
        "residual_probability": _get(version, "residual_probability_of_harm") or _get(version, "residual_occurrence"),
        "residual_risk_level": res_level,
        "residual_risk_acceptability": _get(version, "risk_acceptability"),
        "related_design_input": [],
        "related_design_output": [],
        "verification_reference": [],
        "validation_reference": [],
        "requirement_ids": [],
        "approval_status": "approved" if _get(version, "id") else "draft",
        "approved_by": None,
        "approved_at": None,
        "reviewer_comments": None,
        "ai_generated": False,
        "ai_confidence": None,
        "source_context": "risk_item_version",
        "assumptions": [],
    }
