from __future__ import annotations

from sqlalchemy.orm import Session

from crud import document as document_crud
from schemas import document as document_schemas


REQUIRED_DOCS: list[dict[str, str]] = [
    {"type": "rmp", "name": "Risk Management Plan (RMP)"},
    {"type": "rmf", "name": "Risk Management File (RMF/RMR)"},
    {"type": "risk_acceptability_criteria", "name": "Risk Acceptability Criteria"},
    {"type": "hazard_analysis", "name": "Hazard Analysis"},
    {"type": "residual_risk", "name": "Residual Risk Evaluation"},
    {"type": "benefit_risk_analysis", "name": "Benefit–Risk Analysis"},
    {"type": "risk_controls_doc", "name": "Risk Control Measures Documentation"},
    {"type": "fmea", "name": "FMEA"},
    {"type": "risk_management_review", "name": "Risk Management Review"},
    {"type": "design_dev_plan", "name": "Design & Development Plan"},
    {"type": "design_inputs_doc", "name": "Design Inputs Documentation"},
    {"type": "design_outputs_doc", "name": "Design Outputs Documentation"},
    {"type": "design_reviews", "name": "Design Reviews"},
    {"type": "design_change_record", "name": "Design Change Record"},
    {"type": "vv_plan", "name": "V&V Plan"},
    {"type": "vv_evidence", "name": "V&V Evidence Report"},
    {"type": "validation_summary", "name": "Validation Summary"},
    {"type": "traceability_matrix", "name": "Traceability Matrix"},
    {"type": "change_impact_analysis", "name": "Change Impact Analysis"},
    {"type": "pms_plan", "name": "PMS Plan"},
    {"type": "pms_report", "name": "PMS Report"},
    {"type": "capa", "name": "CAPA"},
    {"type": "usability_risk_analysis", "name": "Usability Risk Analysis"},
    {"type": "hf_validation", "name": "Human Factors Validation"},
    # Quality System & Governance (template + guidance only; no project automation)
    {"type": "document_control_procedure", "name": "Document Control Procedure"},
    {"type": "training_records", "name": "Training Records"},
    {"type": "supplier_risk_assessment", "name": "Supplier Risk Assessment"},
    # Regulatory & Audit Outputs (compile-only; no compliance claims)
    {"type": "essential_requirements_checklist", "name": "Essential Requirements Checklist"},
    {"type": "submission_index", "name": "Submission Index"},
    {"type": "audit_package", "name": "Audit Package"},
]


def _default_content_for(doc_type: str) -> str:
    """
    Minimal deterministic starter content for required SmartQS documents.
    We keep this as plain text for now (existing Document model stores `content` as Text).
    """
    if doc_type == "rmp":
        return (
            "RMP Starter (edit this document):\n"
            "- Scope:\n"
            "- Intended Use:\n"
            "- Components:\n"
            "- Acceptability Profile: default_med_device\n"
            "- Review Roles:\n"
        )
    if doc_type == "rmf":
        return "RMF/RMR export configuration starter. Use RMF page to generate the report and store exports."
    if doc_type == "risk_acceptability_criteria":
        return (
            "Risk Acceptability Criteria starter.\n"
            "Use Project Initialization to draft a conservative template (placeholders only).\n"
        )
    if doc_type == "hazard_analysis":
        return "Hazard Analysis export configuration starter. Use Hazard Analysis page to generate."
    if doc_type == "residual_risk":
        return "Residual Risk Evaluation export configuration starter. Use Residual Risk Evaluation page to generate."
    if doc_type == "benefit_risk_analysis":
        return (
            "Benefit–Risk Analysis starter.\n"
            "Use Project Initialization to draft a conservative structure (no conclusions).\n"
        )
    if doc_type == "risk_controls_doc":
        return "Risk Control Measures Documentation export configuration starter. Use Risk Controls Documentation page to generate."
    if doc_type == "fmea":
        return "FMEA starter. Use FMEA Generator to add rows and save to the project."
    if doc_type == "design_dev_plan":
        return "Design & Development Plan starter. Use Project Initialization to draft a conservative plan template."
    if doc_type == "design_inputs_doc":
        return "Design Inputs Documentation starter. Use Generate New to compile component-scoped requirements and trace evidence."
    if doc_type == "design_outputs_doc":
        return "Design Outputs Documentation starter. Use Generate New to compile component-scoped implementation artifacts and trace evidence."
    if doc_type == "design_reviews":
        return "Design Reviews starter. Use Project Initialization to draft a review record template."
    if doc_type == "design_change_record":
        return "Design Change Record starter. Change entries are appended when project documents get new versions."
    if doc_type == "vv_plan":
        return "V&V Plan starter. Use Generate New to compile verification/validation plan scaffolding and trace links."
    if doc_type == "vv_evidence":
        return "V&V Evidence Report starter. Use Generate New to compile component-scoped verification/validation evidence and trace links."
    if doc_type == "validation_summary":
        return "Validation Summary starter. Use Project Initialization to draft a conservative structure (NOT COMPLETE until evidence exists)."
    if doc_type == "traceability_matrix":
        return "Traceability Matrix export configuration starter."
    if doc_type == "change_impact_analysis":
        return "Change Impact Analysis starter. System-generated impact candidates are appended when project artifacts change versions."
    if doc_type == "pms_plan":
        return "PMS Plan starter. Use Project Initialization to draft a conservative structure (no execution/results)."
    if doc_type == "pms_report":
        return "PMS Report starter. Use Project Initialization to draft a conservative template (DRAFT — no PMS data)."
    if doc_type == "capa":
        return "CAPA starter. Use Project Initialization to draft a CAPA log scaffold (no conclusions/effectiveness)."
    if doc_type == "usability_risk_analysis":
        return "Usability Risk Analysis starter. Use Project Initialization to draft a conservative usability risk scaffold (no execution/results)."
    if doc_type == "hf_validation":
        return "Human Factors Validation starter. Use Project Initialization to draft a conservative HF validation scaffold (DRAFT — NOT EXECUTED)."
    if doc_type == "document_control_procedure":
        return (
            "Document Control Procedure — Template (Draft)\n\n"
            "GENERIC TEMPLATE (no project-specific data)\n"
            "Purpose\n"
            "- Define how documents are created, reviewed, approved, versioned, distributed, and retired.\n\n"
            "1. Scope\n"
            "- Applies to controlled documents and records.\n\n"
            "2. Roles and Responsibilities (placeholders)\n"
            "- Document Owner: (TBD)\n"
            "- Approver(s): (TBD)\n"
            "- QA/RA: (TBD)\n\n"
            "3. Document Lifecycle (placeholders)\n"
            "- Draft → In Review → Approved → Obsolete\n\n"
            "4. Versioning and Change Control (placeholders)\n"
            "- Version increments: (TBD)\n"
            "- Change rationale: (TBD)\n\n"
            "5. Distribution and Access (placeholders)\n"
            "- Storage location: (TBD)\n"
            "- Access control: (TBD)\n\n"
            "6. Training Triggers (placeholders)\n"
            "- When training is required: (TBD)\n"
        )
    if doc_type == "training_records":
        return (
            "Training Records — Template (Draft)\n\n"
            "GENERIC TEMPLATE (no project-specific data)\n"
            "Purpose\n"
            "- Record personnel training for controlled procedures and key roles.\n\n"
            "Training Log (add rows)\n"
            "person | role | procedure/document | training_type | date_completed | trainer | evidence_ref | status\n"
            "----------------------------------------------------------------------------------------------------\n"
            "- (Add entries; do not treat as complete until evidence is attached.)\n"
        )
    if doc_type == "supplier_risk_assessment":
        return (
            "Supplier Risk Assessment — Template (Draft)\n\n"
            "GENERIC TEMPLATE (no project-specific data)\n"
            "Purpose\n"
            "- Evaluate supplier criticality and risk to product quality/safety.\n\n"
            "Supplier Overview (placeholders)\n"
            "- Supplier name: \n"
            "- Supplied item/service: \n"
            "- Criticality: (TBD)\n\n"
            "Risk Factors (placeholders)\n"
            "- Quality history: (TBD)\n"
            "- Regulatory impact: (TBD)\n"
            "- Change notification: (TBD)\n\n"
            "Controls / Monitoring (placeholders)\n"
            "- Qualification activities: (TBD)\n"
            "- Ongoing monitoring: (TBD)\n\n"
            "Decision (placeholder)\n"
            "- Approved / Conditional / Not approved: (TBD)\n"
            "- Rationale: (TBD)\n"
        )
    if doc_type == "essential_requirements_checklist":
        return "Essential Requirements Checklist starter. Use Compile to generate a status-and-links-only checklist (Not assessed by default)."
    if doc_type == "submission_index":
        return "Submission Index starter. Use Compile to list project documents, versions, and statuses."
    if doc_type == "audit_package":
        return "Audit Package starter. Use Compile to list audit-relevant artifacts, versions/statuses, and gaps."
    if doc_type == "risk_management_review":
        return (
            "Risk Management Review starter.\n"
            "Use Project Initialization to draft a meeting-style template (no signatures, no implied approval).\n"
        )
    return "Starter document."


def initialize_project_required_docs(db: Session, project_id: str) -> list[str]:
    """
    Ensure required SmartQS documents exist for a project (idempotent).
    Returns list of created document IDs.
    """
    existing = document_crud.get_documents_by_project(db, project_id)
    existing_types = {d.type for d in existing}

    created_ids: list[str] = []
    for spec in REQUIRED_DOCS:
        if spec["type"] in existing_types:
            continue

        doc = document_schemas.DocumentCreate(
            project_id=project_id,
            name=spec["name"],
            type=spec["type"],
            status="draft",
            content=_default_content_for(spec["type"]),
        )
        created = document_crud.create_document(db, doc)
        created_ids.append(created.id)

    return created_ids


