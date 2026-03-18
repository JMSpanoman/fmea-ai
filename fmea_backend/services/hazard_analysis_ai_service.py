"""
AI completion for Hazard Analysis items — ISO 14971-style.
Fills missing fields via LLM; does not overwrite approved or human-entered content.
"""
from __future__ import annotations
import os
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default structured output for fallback (component-specific placeholders)
DEFAULT_HA_JSON_KEYS = [
    "hazard_category", "hazard", "foreseeable_sequence_of_events", "hazardous_situation",
    "harm", "affected_user", "failure_mode", "cause_of_failure", "clinical_effect",
    "operating_mode", "use_environment", "initial_severity", "initial_probability",
    "initial_risk_level", "risk_control_measures", "risk_control_type",
    "control_implementation_notes", "residual_severity", "residual_probability",
    "residual_risk_level", "residual_risk_acceptability", "related_design_input",
    "related_design_output", "verification_reference", "validation_reference",
    "requirement_ids", "assumptions", "ai_confidence",
]


def _load_prompt_template() -> str:
    base = Path(__file__).resolve().parent.parent.parent
    path = base / "ai_prompts" / "hazard_analysis_iso14971_prompt.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _build_context(
    device_type: Optional[str] = None,
    component_name: Optional[str] = None,
    intended_use: Optional[str] = None,
    use_environment: Optional[str] = None,
    fmea_row: Optional[Dict[str, Any]] = None,
) -> str:
    parts = []
    if device_type:
        parts.append(f"Device type: {device_type}")
    if component_name:
        parts.append(f"Component: {component_name}")
    if intended_use:
        parts.append(f"Intended use: {intended_use}")
    if use_environment:
        parts.append(f"Use environment: {use_environment}")
    if fmea_row:
        parts.append("Existing FMEA data (use to prefill where possible):")
        for k in ("failure_mode", "cause", "effect", "severity", "probability", "mitigation"):
            v = fmea_row.get(k)
            if v is not None and str(v).strip():
                parts.append(f"  - {k}: {v}")
    return "\n".join(parts) if parts else "No additional context provided."


def _parse_json_from_response(text: str) -> Optional[Dict[str, Any]]:
    if not (text or "").strip():
        return None
    text = text.strip()
    # Strip markdown code block if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _fallback_hazard_analysis_json(
    component_name: Optional[str] = None,
    hazard_category: Optional[str] = None,
    fmea_row: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Deterministic fallback when OpenAI is not configured."""
    comp = (component_name or "Device component").strip()
    cat = (hazard_category or "Technical").strip()
    out = {
        "hazard_category": cat,
        "hazard": f"Failure or malfunction of {comp} affecting safety-related function",
        "foreseeable_sequence_of_events": f"Fault in {comp} leads to incorrect output or loss of function; user or patient is exposed before detection or correction.",
        "hazardous_situation": f"Patient or user relies on device function while {comp} has failed or is operating outside specification.",
        "harm": "Physical injury or deterioration of health consistent with device intended use and failure mode (specific harm to be confirmed by clinical evaluation).",
        "affected_user": "Patient",
        "failure_mode": fmea_row.get("failure_mode") if fmea_row else f"Loss of or degradation in {comp} function",
        "cause_of_failure": fmea_row.get("cause") if fmea_row else f"Design, manufacturing, or use-related cause specific to {comp} (to be documented).",
        "clinical_effect": fmea_row.get("effect") if fmea_row else "Adverse clinical outcome; severity depends on timing and mitigations.",
        "operating_mode": "Normal operation",
        "use_environment": "Clinical or home use as specified in intended use",
        "initial_severity": int(fmea_row["severity"]) if fmea_row and fmea_row.get("severity") is not None else 5,
        "initial_probability": int(fmea_row["probability"]) if fmea_row and fmea_row.get("probability") is not None else 3,
        "initial_risk_level": "Medium",
        "risk_control_measures": [f"Design and verification of {comp}", "User information and training", "Post-market monitoring"] if not (fmea_row and fmea_row.get("mitigation")) else [str(fmea_row.get("mitigation", ""))],
        "risk_control_type": ["inherent_safety_by_design", "protective_measures", "information_for_safety"],
        "control_implementation_notes": "To be completed with design and verification references.",
        "residual_severity": 3,
        "residual_probability": 2,
        "residual_risk_level": "Low",
        "residual_risk_acceptability": "acceptable",
        "related_design_input": [],
        "related_design_output": [],
        "verification_reference": [],
        "validation_reference": [],
        "requirement_ids": [],
        "assumptions": ["Fallback draft; replace with project-specific analysis and evidence."],
        "ai_confidence": "low",
    }
    return out


def generate_hazard_analysis_item_with_ai(
    device_type: Optional[str] = None,
    component_name: Optional[str] = None,
    intended_use: Optional[str] = None,
    use_environment: Optional[str] = None,
    fmea_row: Optional[Dict[str, Any]] = None,
    hazard_category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Call LLM to produce one hazard analysis item as JSON.
    Returns a dict with keys matching HazardAnalysisItem / AI prompt schema.
    Uses fallback if OPENAI_API_KEY is not set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    prompt_template = _load_prompt_template()
    context = _build_context(
        device_type=device_type,
        component_name=component_name,
        intended_use=intended_use,
        use_environment=use_environment,
        fmea_row=fmea_row,
    )
    if not api_key or not prompt_template:
        return _fallback_hazard_analysis_json(
            component_name=component_name,
            hazard_category=hazard_category,
            fmea_row=fmea_row,
        )
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        msg_content = (
            f"{prompt_template}\n\n"
            "Input context:\n"
            f"{context}\n\n"
            "Generate exactly one JSON object for one hazard analysis item. Output only valid JSON."
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": msg_content}],
            temperature=0.3,
            max_tokens=2000,
        )
        text = ""
        if response.choices:
            text = (response.choices[0].message.content or "").strip()
        parsed = _parse_json_from_response(text)
        if parsed and isinstance(parsed, dict):
            # Normalize list fields
            for key in ("risk_control_measures", "risk_control_type", "related_design_input",
                        "related_design_output", "verification_reference", "validation_reference",
                        "requirement_ids", "assumptions"):
                if key in parsed and not isinstance(parsed.get(key), list):
                    if parsed[key] is None:
                        parsed[key] = []
                    else:
                        parsed[key] = [str(parsed[key])]
            parsed.setdefault("ai_confidence", "medium")
            return parsed
    except Exception:
        pass
    return _fallback_hazard_analysis_json(
        component_name=component_name,
        hazard_category=hazard_category,
        fmea_row=fmea_row,
    )


def merge_ai_into_item(
    existing: Dict[str, Any],
    ai_output: Dict[str, Any],
    *,
    only_blank: bool = True,
    approved_statuses: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Merge AI-generated fields into existing item. If only_blank is True,
    do not overwrite non-empty fields. Never overwrite approved items' key fields
    when approval_status is in approved_statuses (e.g. ["approved"]).
    """
    approved_statuses = approved_statuses or ["approved"]
    out = dict(existing)
    for key in DEFAULT_HA_JSON_KEYS:
        if key not in ai_output:
            continue
        new_val = ai_output[key]
        cur_val = out.get(key)
        if only_blank and cur_val is not None and cur_val != "" and cur_val != []:
            continue
        if out.get("approval_status") in approved_statuses and key in (
            "hazard", "harm", "failure_mode", "foreseeable_sequence_of_events",
            "residual_risk_acceptability", "initial_severity", "initial_probability",
        ):
            continue
        out[key] = new_val
    out["ai_generated"] = True
    out["ai_confidence"] = ai_output.get("ai_confidence") or out.get("ai_confidence")
    return out
