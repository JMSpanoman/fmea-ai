"""
AI review hook templates for CAPA workflow.
These are prompts only — the application must not auto-close CAPA or auto-confirm effectiveness.
"""

CAPA_AI_HOOKS: dict[str, dict[str, str]] = {
    "problem_statement_review": {
        "title": "Problem statement quality",
        "prompt": (
            "Review the CAPA problem statement. Is it specific, measurable, and free of assumed root causes? "
            "List concrete gaps and suggested edits. Do not conclude regulatory acceptability."
        ),
    },
    "root_cause_challenge": {
        "title": "Root cause challenge",
        "prompt": (
            "What objective evidence supports the stated root cause? "
            "Could this be a symptom rather than the deepest cause? Cite missing evidence types."
        ),
    },
    "missing_evidence_detection": {
        "title": "Missing evidence",
        "prompt": (
            "List objective evidence that should exist for this CAPA stage (containment, RCA, actions, effectiveness) "
            "but appears missing or unreferenced."
        ),
    },
    "systemic_scope_challenge": {
        "title": "Systemic scope",
        "prompt": (
            "Given the problem and containment, could this issue be systemic? "
            "Where else could this occur (processes, products, sites, suppliers)?"
        ),
    },
    "capa_risk_consistency": {
        "title": "CAPA–risk consistency",
        "prompt": (
            "Compare CAPA corrective/preventive actions and linked risk/FMEA references. "
            "Are risk controls and residual risk documentation consistent with the actions taken?"
        ),
    },
}


def list_ai_hook_prompts() -> list[dict[str, str]]:
    """Expose hooks to API / UI."""
    return [{"id": k, **v} for k, v in CAPA_AI_HOOKS.items()]
