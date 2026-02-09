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
        "benefit_risk_analysis": {
            "purpose_text": (
                "Documents the structured rationale comparing expected clinical benefits to residual risks "
                "(ISO 14971 benefit-risk), including consideration of state-of-the-art alternatives and post-market data."
            ),
            "population_text": (
                "SmartQS uses Project Setup context (intended use, clinical environment, components) plus any available evidence "
                "(FMEA rows, residual risk evaluations, PMS signals, usability/non-clinical artifacts) to draft a conservative example. "
                "It does not invent clinical outcomes, complaint rates, or market comparisons."
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
        "vv_plan": {
            "purpose_text": (
                "Defines the planned verification and validation approach, including high-level activities, methods, and traceability expectations."
            ),
            "population_text": (
                "SmartQS scaffolds a conservative V&V plan from Design Inputs and Risk Controls (verification methods where available). "
                "All activities remain 'Planned' until you execute and record evidence."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "vv_evidence": {
            "purpose_text": (
                "Provides slots to record objective evidence for each planned V&V activity (reports, files, results, deviations)."
            ),
            "population_text": (
                "SmartQS mirrors the V&V Plan activities as evidence slots. "
                "Slots are 'Not Executed' by default until evidence is uploaded/linked and results are recorded."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "validation_summary": {
            "purpose_text": (
                "Summarizes the validation approach and evidence at a high level. This document cannot be finalized until validation evidence exists."
            ),
            "population_text": (
                "SmartQS creates a structure-only draft using Project Setup context and references to the V&V Evidence Report and Residual Risk Evaluation."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "traceability_matrix": {
            "purpose_text": (
                "Shows end-to-end traceability across components, risks, controls, design inputs/outputs, and planned verification."
            ),
            "population_text": (
                "SmartQS builds a deterministic traceability view from your Components, FMEA rows, Risk Items/Controls, Design Inputs/Outputs, and V&V Plan/Evidence scaffolds. "
                "Gaps are highlighted but never auto-fixed."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "change_impact_analysis": {
            "purpose_text": (
                "Lists candidate impacted artifacts when upstream items change, to support human-led impact assessment and decision-making."
            ),
            "population_text": (
                "SmartQS appends impact-candidate entries when project documents create new versions (and other key changes where available). "
                "It never infers conclusions; impact summary/decision/actions must be completed by the team."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "pms_plan": {
            "purpose_text": (
                "Defines the planned post-market surveillance approach: data sources, review cadence, signal detection, and escalation workflow."
            ),
            "population_text": (
                "SmartQS drafts a conservative PMS Plan scaffold using Project Setup context and references to risk artifacts. "
                "It does not invent thresholds or imply that PMS data exists."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "pms_report": {
            "purpose_text": (
                "Provides a template to summarize post-market data reviewed during a defined reporting period."
            ),
            "population_text": (
                "SmartQS provides a structure-only report template. Populate after post-market data exists; "
                "this draft must not be treated as evidence of data review."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "capa": {
            "purpose_text": (
                "Tracks corrective and preventive actions (CAPA): triggers, containment, root cause, actions, and effectiveness plan."
            ),
            "population_text": (
                "SmartQS provides a CAPA log scaffold. Trigger references can later be linked to quality events/complaints/NCRs where available. "
                "No effectiveness confirmation is included without objective evidence."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "usability_risk_analysis": {
            "purpose_text": (
                "Identifies use-related hazards and use errors (UI, training, labeling, foreseeable misuse) and links them to controls."
            ),
            "population_text": (
                "SmartQS drafts a structure-only scaffold using Project Setup context and references to core risk artifacts. "
                "Do not treat this as evidence of human factors work until tasks are analyzed and controls are defined."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "hf_validation": {
            "purpose_text": (
                "Provides a scaffold to plan and record human factors validation (critical tasks, study design, evidence slots)."
            ),
            "population_text": (
                "SmartQS creates a draft, not-executed template. Attach protocol/results and record deviations when studies are performed."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        # Quality System & Governance (template-only)
        "document_control_procedure": {
            "purpose_text": (
                "Defines how controlled documents are created, reviewed, approved, versioned, distributed, and retired."
            ),
            "population_text": (
                "This is a generic procedure template. SmartQS does not auto-populate it from project data. "
                "Tailor it to your QMS and record approvals separately."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "training_records": {
            "purpose_text": (
                "Stores evidence that personnel have been trained on controlled procedures/documents."
            ),
            "population_text": (
                "This is a generic training log template. Add entries and attach evidence as training is performed. "
                "SmartQS does not auto-fill training completion."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "supplier_risk_assessment": {
            "purpose_text": (
                "Documents supplier qualification and risk assessment to ensure supplier controls are appropriate."
            ),
            "population_text": (
                "This is a generic supplier assessment template. Fill in supplier-specific details and decisions. "
                "SmartQS does not auto-assess supplier risk."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        # Regulatory & Audit Outputs (compile-only)
        "essential_requirements_checklist": {
            "purpose_text": (
                "Provides a checklist view mapping requirements to available project evidence references."
            ),
            "population_text": (
                "SmartQS compiles a links-and-status-only checklist on user request. "
                "All items default to 'Not assessed' and no compliance claims are made."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "submission_index": {
            "purpose_text": (
                "Lists project documents, their status, and version information for submission packaging."
            ),
            "population_text": (
                "SmartQS compiles the index on user request by listing existing project documents and metadata only."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "audit_package": {
            "purpose_text": (
                "Provides an audit package view: a structured list of audit-relevant artifacts and their current status/version."
            ),
            "population_text": (
                "SmartQS compiles this package on user request by indexing documents and summarizing gaps (e.g., Not started, traceability gaps). "
                "It does not create new evidence or claims."
            ),
            "ai_available": False,
            "ai_button_text": "",
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
        # Design Controls docs: conservative deterministic drafting; do not encourage AI for these by default.
        "design_dev_plan": {
            "purpose_text": (
                "Plans design and development activities, responsibilities, reviews, and lifecycle deliverables."
            ),
            "population_text": (
                "SmartQS drafts a conservative plan skeleton from Project Setup and references related documents. "
                "You tailor timelines, roles, and deliverables and record approvals separately."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "design_reviews": {
            "purpose_text": (
                "Records design review meetings (agenda, attendees, reviewed artifacts, issues, and actions)."
            ),
            "population_text": (
                "SmartQS drafts a review record template and auto-lists relevant artifacts (Design Inputs/Outputs, risk docs, V&V plan). "
                "Dates, attendees, and approvals must be entered explicitly by the team."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
        "design_change_record": {
            "purpose_text": (
                "Tracks design changes and their candidate impacted artifacts for later assessment and approval."
            ),
            "population_text": (
                "SmartQS appends a new change entry when a project document gets a new version. "
                "It never infers conclusions; it only lists candidate affected artifacts for review."
            ),
            "ai_available": False,
            "ai_button_text": "",
        },
    }

    reg: Dict[str, Dict[str, Any]] = {}
    for t in doc_types:
        entry = {**base, **overrides.get(t, {})}
        # ensure required keys exist
        entry["purpose_text"] = str(entry.get("purpose_text") or "")
        entry["population_text"] = str(entry.get("population_text") or "")
        # User request: enable AI for all document types.
        # Keep RMF compiled-only (it must not invent content).
        if (t or "").strip().lower() == "rmf":
            entry["ai_available"] = False
            entry["ai_button_text"] = ""
        else:
            entry["ai_available"] = True
            entry["ai_button_text"] = str(entry.get("ai_button_text") or "Generate AI sample") or "Generate AI sample"
        reg[t] = entry

    return reg

