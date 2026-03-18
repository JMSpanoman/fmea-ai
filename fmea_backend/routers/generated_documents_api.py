"""
Generated documents API.

GET /api/generated-documents/:id
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from models.generated_document import GeneratedDocument
from models.device import Device
from crud import project as project_crud

router = APIRouter(
    prefix="/api/generated-documents",
    tags=["Generated Documents API"],
    dependencies=[Depends(require_pro)],
)


def _ensure_document_access(db: Session, doc_id: str, user_id: str) -> GeneratedDocument:
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Generated document not found")
    device = db.query(Device).filter(Device.id == doc.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if not project_crud.get_project(db, device.project_id, user_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return doc


@router.get("/{doc_id}")
def get_generated_document(
    doc_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a generated document by ID. User must have access to the document's device project."""
    doc = _ensure_document_access(db, doc_id, current_user.id)
    return {
        "id": doc.id,
        "device_id": doc.device_id,
        "document_type": doc.document_type,
        "title": doc.title,
        "content_json": doc.content_json,
        "content_markdown": doc.content_markdown,
        "version": doc.version,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }
