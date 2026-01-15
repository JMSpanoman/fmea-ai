from __future__ import annotations

from typing import Any, Dict


def get_document_guidance_registry() -> Dict[str, Dict[str, Any]]:
    """
    Central, read-only guidance registry keyed by document_type.

    Notes:
    - This is intentionally plain text for non-quality users.
    - Keep language regulator-accurate but simple.
    - `ai_available` is a product capability flag; actual runtime availability still depends on AI config.
    """

    # Canonical doc types requested by the user (keep in sync with frontend guidance header).
    doc_types = [
        "rmp",
        "risk_acceptability_criteria",
        "hazard_analysis",
        "fmea",
        "risk_controls_doc",
        "residual_risk",
        "benefit_risk_analysis",
        "rmf",
        "risk_management_review",
        "design_dev_plan",
        "design_inputs_doc",
        "design_outputs_doc",
        "design_reviews",
        "design_change_record",
        "vv_plan",
        "vv_evidence",
        "validation_summary",
        "clinical_evaluation",
        "traceability_matrix",
        "change_impact_analysis",
        "pms_plan",
        "pms_report",
        "capa",
        "usability_risk_analysis",
        "hf_validation",
        "document_control_procedure",
        "training_records",
        "supplier_risk_assessment",
        "essential_requirements_checklist",
        "submission_index",
        "audit_package",
    ]

    # Defaults for unspecified docs.
    base = {
        "purpose_text": (
            "This document captures evidence and decisions for this part of the QMS. "
            "Use it to record the project’s planned work, outputs, and approvals in an audit-friendly way."
        ),
        "population_text": (
            "In SmartQS, parts of this document may be drafted using Project Setup (device basics + components) "
            "and by linking related records (e.g., FMEA rows, risk controls, risk items). "
            "You can always edit and approve the final content."
        ),
        "ai_available": True,
        "ai_button_text": "Generate AI sample",
    }

    # Overrides for key risk docs (these are the most visible to non-quality users).
    overrides: Dict[str, Dict[str, Any]] = {
        "rmp": {
            "purpose_text": (
                "Defines how risk management will be performed for this project (scope, roles, methods, and planned activities)."
            ),
            "population_text": (
                "SmartQS drafts an initial RMP using Project Setup (device description, intended use, user population, environment) "
                "and your component list. You review, tailor, and approve it."
            ),
        },
        "hazard_analysis": {
            "purpose_text": (
                "Identifies hazards and hazardous situations relevant to the device and its use. "
                "This supports ISO 14971 hazard identification."
            ),
            "population_text": (
                "SmartQS can seed starter hazards from Project Setup (intended use/environment + components/tags). "
                "As you add risks and controls, related evidence is linked for traceability."
            ),
        },
        "fmea": {
            "purpose_text": (
                "Analyzes potential failure modes, causes, and effects. Used to support risk analysis and prioritization."
            ),
            "population_text": (
                "SmartQS creates baseline rows from your component list, then you refine failure modes/effects/causes. "
                "Optional AI scoring can populate draft hazard and S/O/D placeholders (requires explicit actions elsewhere)."
            ),
        },
        "risk_controls_doc": {
            "purpose_text": (
                "Documents risk control measures and how they are verified. Supports ISO 14971 risk control requirements."
            ),
            "population_text": (
                "SmartQS aggregates controls from structured Risk Controls plus linked controls from FMEA/Risk Items, "
                "and shows verification method placeholders and trace links to V&V where applicable."
            ),
        },
        "residual_risk": {
            "purpose_text": (
                "Summarizes residual risk after controls and supports acceptability decisions."
            ),
            "population_text": (
                "SmartQS drafts the structure from Project Setup and links to the underlying risk analysis and controls. "
                "Risk scoring/acceptability must be reviewed and approved by the team."
            ),
        },
        "traceability_matrix": {
            "purpose_text": (
                "Provides traceability across components, risks, controls, and verification activities."
            ),
            "population_text": (
                "SmartQS links Components → FMEA rows and connects Design Inputs/Outputs and V&V activities when available."
            ),
        },
        "rmf": {
            "purpose_text": (
                "A compiled, evidence-based Risk Management File that references authoritative risk documents."
            ),
            "population_text": (
                "SmartQS compiles the RMF by linking to RMP, Hazard Analysis, FMEA, Risk Controls, Residual Risk, and reviews. "
                "This document is read-only intent and should not be manually edited."
            ),
            "ai_available": False,  # must not invent content
            "ai_button_text": "",
        },
    }

    reg: Dict[str, Dict[str, Any]] = {}
    for t in doc_types:
        entry = {**base, **overrides.get(t, {})}
        # ensure required keys exist
        entry["purpose_text"] = str(entry.get("purpose_text") or "")
        entry["population_text"] = str(entry.get("population_text") or "")
        entry["ai_available"] = bool(entry.get("ai_available", False))
        entry["ai_button_text"] = str(entry.get("ai_button_text") or "Generate AI sample")
        reg[t] = entry

    return reg

