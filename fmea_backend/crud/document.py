from sqlalchemy.orm import Session
from models.document import Document, DocumentVersion
from schemas.document import DocumentCreate, DocumentUpdate
from typing import List, Optional
import uuid
from datetime import datetime, timezone


def _safe_str(v: object) -> str:
    return "" if v is None else str(v)


def _design_change_record_entry_marker(*, source_doc_id: str, version_id: str, version_no: int) -> str:
    return f"[DESIGN_CHANGE_ENTRY source_doc_id={source_doc_id} version_id={version_id} version_no={version_no}]"


def _candidate_impacted_types(source_type: str) -> List[str]:
    t = (source_type or "").lower().strip()
    if t == "design_inputs_doc":
        return ["design_outputs_doc", "traceability_matrix", "vv_plan"]
    if t in {"hazard_analysis", "fmea"}:
        return ["risk_controls_doc", "residual_risk", "traceability_matrix"]
    if t == "risk_controls_doc":
        return ["vv_plan", "residual_risk", "traceability_matrix"]
    return []


def _append_design_change_entry(
    db: Session,
    *,
    project_id: str,
    source_doc: Document,
    version_obj: DocumentVersion,
) -> None:
    """
    Append a new change entry into the project's design_change_record document.

    Rules:
    - Must be idempotent (no duplicate entry for the same version id/no)
    - Must not recurse infinitely (skip when the source doc is the change record itself)
    - Must not infer impact conclusions; only list candidate affected artifacts
    """
    source_type = (_safe_str(getattr(source_doc, "type", ""))).lower()
    if source_type == "design_change_record":
        return

    # Ensure the change record doc exists.
    dcr = get_document_by_type(db, project_id=project_id, doc_type="design_change_record")
    if not dcr:
        dcr = create_document(
            db,
            DocumentCreate(
                project_id=project_id,
                name="Design Change Record",
                type="design_change_record",
                status="draft",
                content="Design Change Record starter. Change entries are appended when project documents get new versions.",
            ),
        )

    marker = _design_change_record_entry_marker(
        source_doc_id=_safe_str(getattr(source_doc, "id", "")),
        version_id=_safe_str(getattr(version_obj, "id", "")),
        version_no=int(getattr(version_obj, "version", 0) or 0),
    )
    existing = dcr.content or ""
    if marker in existing:
        return

    # Best-effort artifact list for the project
    docs = get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    impacted_types = _candidate_impacted_types(source_type)
    impacted_lines: List[str] = []
    for t in impacted_types:
        doc = by_type.get(t)
        if not doc:
            impacted_lines.append(f"- {t}: (not present yet)")
        else:
            impacted_lines.append(
                f"- {t}: doc_id={doc.id} (status={doc.status}, version=v{doc.version})"
            )
    if not impacted_lines:
        impacted_lines = ["- (No candidate impacted artifacts listed for this change type)"]

    ts = _safe_str(getattr(version_obj, "created_at", "")) or datetime.now(timezone.utc).isoformat()
    entry = (
        "\n"
        + ("-" * 72)
        + "\n"
        + "Design Change Entry — Draft\n"
        + marker
        + "\n"
        + f"Timestamp: {ts}\n"
        + f"Changed document: {source_doc.name} (type={source_type}, doc_id={source_doc.id})\n"
        + f"New version: v{version_obj.version} (version_id={version_obj.id})\n"
        + "\n"
        + "Change description: (blank — to be completed)\n"
        + "Rationale: (blank — to be completed)\n"
        + "Impact assessment: (blank — to be completed)\n"
        + "\n"
        + "Affected artifacts (candidates; not assessed):\n"
        + "\n".join(impacted_lines)
        + "\n"
    )

    # Append (never overwrite).
    new_content = (existing.rstrip() + "\n" + entry).lstrip() if existing else entry.lstrip()
    update_document(
        db,
        dcr.id,
        DocumentUpdate(content=new_content, status="draft"),
        project_id,
    )

def create_document(db: Session, document: DocumentCreate) -> Document:
    """Create a new document"""
    db_doc = Document(
        id=str(uuid.uuid4()),
        project_id=document.project_id,
        name=document.name,
        type=document.type,
        content=document.content,
        version=1,
        status=document.status,
        ai_metadata=document.ai_metadata
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Create initial version
    create_document_version(db, db_doc.id, 1, db_doc.content, {})
    
    return db_doc

def get_documents_by_project(db: Session, project_id: str) -> List[Document]:
    """Get all documents for a project"""
    return db.query(Document).filter(Document.project_id == project_id).all()

def get_document(db: Session, document_id: str, project_id: str) -> Optional[Document]:
    """Get a specific document"""
    return db.query(Document).filter(
        Document.id == document_id,
        Document.project_id == project_id
    ).first()

def get_document_by_type(db: Session, *, project_id: str, doc_type: str) -> Optional[Document]:
    """Get the most recent document by type for a project (current row in documents table)."""
    t = (doc_type or "").strip().lower()
    if not t:
        return None
    return (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.type == t)
        .first()
    )

def update_document(db: Session, document_id: str, document: DocumentUpdate, project_id: str) -> Optional[Document]:
    """Update a document"""
    db_doc = get_document(db, document_id, project_id)
    if not db_doc:
        return None
    
    old_content = db_doc.content
    update_data = document.model_dump(exclude_unset=True) if hasattr(document, 'model_dump') else document.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_doc, field, value)
    
    created_version: Optional[DocumentVersion] = None
    # If content changed, create new version
    if 'content' in update_data and update_data['content'] != old_content:
        db_doc.version += 1
        # Guardrail: editing an approved document creates a new draft version
        if db_doc.status == "approved":
            db_doc.status = "draft"
        changes = {"field": "content", "old": old_content, "new": update_data['content']}
        created_version = create_document_version(db, document_id, db_doc.version, update_data['content'], changes)
    
    db_doc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_doc)

    # Design Controls: append Design Change Record entry for new versions (best-effort).
    # Note: never log changes to the Design Change Record itself to avoid recursion/noise.
    try:
        if created_version is not None:
            src_type = (_safe_str(getattr(db_doc, "type", ""))).lower().strip()
            if src_type != "design_change_record":
                _append_design_change_entry(db, project_id=project_id, source_doc=db_doc, version_obj=created_version)
    except Exception:
        # Never block the main write path for auxiliary logging.
        pass

    # Traceability & Impact: append Change Impact Analysis entry for new versions (best-effort).
    try:
        if created_version is not None:
            src_type = (_safe_str(getattr(db_doc, "type", ""))).lower().strip()
            if src_type not in {"change_impact_analysis", "design_change_record"}:
                from services.change_impact import record_change_impact_for_document_version
                record_change_impact_for_document_version(db, project_id=project_id, source_doc=db_doc, version_obj=created_version)
    except Exception:
        # Never block the main write path for auxiliary logging.
        pass
    return db_doc


def get_document_version_by_no(db: Session, document_id: str, version: int) -> Optional[DocumentVersion]:
    """Get a specific document version"""
    return db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id,
        DocumentVersion.version == version
    ).first()

def delete_document(db: Session, document_id: str, project_id: str) -> bool:
    """Delete a document"""
    db_doc = get_document(db, document_id, project_id)
    if not db_doc:
        return False
    
    db.delete(db_doc)
    db.commit()
    return True

def create_document_version(db: Session, document_id: str, version: int, content: Optional[str], changes: dict) -> DocumentVersion:
    """Create a document version"""
    db_version = DocumentVersion(
        id=str(uuid.uuid4()),
        document_id=document_id,
        version=version,
        content=content,
        changes=changes
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

def get_document_versions(db: Session, document_id: str) -> List[DocumentVersion]:
    """Get all versions of a document"""
    return db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(DocumentVersion.version.desc()).all()

def approve_document(db: Session, document_id: str, project_id: str) -> Optional[Document]:
    """Approve a document (changes status to approved)"""
    db_doc = get_document(db, document_id, project_id)
    if not db_doc:
        return None
    
    if db_doc.status != "approved":
        db_doc.status = "approved"
        db.commit()
        db.refresh(db_doc)
    
    return db_doc

