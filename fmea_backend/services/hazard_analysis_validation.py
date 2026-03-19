"""
Validation and business rules for Hazard Analysis items (ISO 14971).
- Hazard must be specific, not generic
- Failure mode must not be empty
- Sequence of events must be plausible (not N/A)
- Harm must be specific
- Severity/probability populated
- Risk controls for non-negligible risks
- Residual risk present when controls present
"""
from typing import Any, Dict, List, Tuple, Optional

GENERIC_PHRASES = [
    "potential hazard related to general",
    "issue in component could lead to hazardous situation",
    "potential injury or harm to user/patient/operator",
    "n/a",
    "na ",
    "tbd",
    "to be determined",
]


def _is_generic(text: Optional[str]) -> bool:
    if not text or not str(text).strip():
        return True
    lower = str(text).strip().lower()
    for phrase in GENERIC_PHRASES:
        if phrase in lower:
            return True
    if lower in ("n/a", "na", "—", "-", "."):
        return True
    return False


def validate_hazard_analysis_item(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a hazard analysis item (dict or ORM-like). Returns (valid, list of error messages).
    """
    errors: List[str] = []
    hazard = (data.get("hazard") or "").strip()
    failure_mode = (data.get("failure_mode") or "").strip()
    sequence = (data.get("foreseeable_sequence_of_events") or data.get("sequence_of_events") or "").strip()
    harm = (data.get("harm") or "").strip()
    initial_severity = data.get("initial_severity")
    initial_probability = data.get("initial_probability") if data.get("initial_probability") is not None else data.get("initial_occurrence")
    risk_controls = data.get("risk_control_measures")
    structured_controls = data.get("risk_controls") or []
    residual_severity = data.get("residual_severity")
    residual_probability = data.get("residual_probability") if data.get("residual_probability") is not None else data.get("residual_occurrence")
    residual_acceptability = data.get("residual_risk_acceptability") or data.get("risk_acceptability_decision")
    residual_justification = (data.get("risk_acceptability_justification") or "").strip()
    benefit_risk_required = bool(data.get("benefit_risk_analysis_required"))
    benefit_risk_justification = (data.get("benefit_risk_justification") or "").strip()

    if not hazard:
        errors.append("Hazard is required.")
    elif _is_generic(hazard):
        errors.append("Hazard must be specific; avoid generic phrases.")

    if not failure_mode:
        errors.append("Failure mode must not be empty.")

    if not sequence or _is_generic(sequence):
        errors.append("Sequence of events must be plausible and not N/A.")

    if not harm or _is_generic(harm):
        errors.append("Harm must be specific.")

    if initial_severity is None and initial_probability is None:
        errors.append("Initial severity and/or probability should be populated.")

    has_controls = bool(risk_controls and (isinstance(risk_controls, list) and len(risk_controls) > 0 or isinstance(risk_controls, str) and risk_controls.strip()))
    has_structured_controls = isinstance(structured_controls, list) and len(structured_controls) > 0
    if has_structured_controls:
        for idx, c in enumerate(structured_controls):
            if not isinstance(c, dict):
                errors.append(f"Risk control #{idx + 1} must be an object.")
                continue
            if not (c.get("control_type") or "").strip():
                errors.append(f"Risk control #{idx + 1} requires control_type.")
            if not (c.get("control_description") or "").strip():
                errors.append(f"Risk control #{idx + 1} requires control_description.")
    risk_high = (initial_severity is not None and initial_severity >= 7) or (initial_probability is not None and initial_probability >= 7)
    if risk_high and not (has_controls or has_structured_controls):
        errors.append("Risk controls should exist for non-negligible risks (structured or legacy).")

    if (has_controls or has_structured_controls) and residual_severity is None and residual_probability is None and not residual_acceptability:
        errors.append("Residual risk fields should be present when controls are applied.")

    if residual_acceptability and not residual_justification:
        errors.append("Risk acceptability justification is required when decision is set.")

    high_or_not_acceptable = False
    if isinstance(residual_acceptability, str):
        low = residual_acceptability.strip().lower()
        high_or_not_acceptable = low in {"not_acceptable", "not acceptable", "unacceptable", "high", "high_risk"}
    if isinstance(residual_severity, int) and residual_severity >= 4:
        high_or_not_acceptable = True
    if high_or_not_acceptable and not benefit_risk_required:
        errors.append("Benefit-risk analysis flag is required for high/not acceptable residual risk.")
    if benefit_risk_required and not benefit_risk_justification:
        errors.append("Benefit-risk justification is required when benefit-risk analysis is flagged.")

    return (len(errors) == 0, errors)


def should_flag_for_manual_review(data: Dict[str, Any]) -> bool:
    """Severe harms or low AI confidence should trigger reviewer attention."""
    harm = (data.get("harm") or "").strip().lower()
    severe_words = ["death", "fatal", "permanent injury", "irreversible", "cardiac arrest", "life-threatening"]
    if any(w in harm for w in severe_words):
        return True
    if (data.get("ai_confidence") or "").lower() in ("low", "medium"):
        return True
    if data.get("initial_severity") is not None and data.get("initial_severity") >= 8:
        return True
    return False
