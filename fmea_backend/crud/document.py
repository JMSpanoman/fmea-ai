from sqlalchemy.orm import Session
from models.document import Document, DocumentVersion
from schemas.document import DocumentCreate, DocumentUpdate
from typing import List, Optional
import uuid
from datetime import datetime, timezone

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
    
    # If content changed, create new version
    if 'content' in update_data and update_data['content'] != old_content:
        db_doc.version += 1
        # Guardrail: editing an approved document creates a new draft version
        if db_doc.status == "approved":
            db_doc.status = "draft"
        changes = {"field": "content", "old": old_content, "new": update_data['content']}
        create_document_version(db, document_id, db_doc.version, update_data['content'], changes)
    
    db_doc.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_doc)
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

