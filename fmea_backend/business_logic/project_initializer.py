from __future__ import annotations

from sqlalchemy.orm import Session

from crud import document as document_crud
from schemas import document as document_schemas


REQUIRED_DOCS: list[dict[str, str]] = [
    {"type": "rmp", "name": "Risk Management Plan (RMP)"},
    {"type": "rmf", "name": "Risk Management File (RMF/RMR)"},
    {"type": "hazard_analysis", "name": "Hazard Analysis"},
    {"type": "residual_risk", "name": "Residual Risk Evaluation"},
    {"type": "risk_controls_doc", "name": "Risk Control Measures Documentation"},
    {"type": "fmea", "name": "FMEA"},
    {"type": "traceability_matrix", "name": "Traceability Matrix"},
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
    if doc_type == "hazard_analysis":
        return "Hazard Analysis export configuration starter. Use Hazard Analysis page to generate."
    if doc_type == "residual_risk":
        return "Residual Risk Evaluation export configuration starter. Use Residual Risk Evaluation page to generate."
    if doc_type == "risk_controls_doc":
        return "Risk Control Measures Documentation export configuration starter. Use Risk Controls Documentation page to generate."
    if doc_type == "fmea":
        return "FMEA starter. Use FMEA Generator to add rows and save to the project."
    if doc_type == "traceability_matrix":
        return "Traceability Matrix export configuration starter."
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


