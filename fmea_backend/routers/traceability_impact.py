from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from crud import project as project_crud
from crud import document as document_crud
from schemas.document import DocumentUpdate
from services.traceability_builder import build_traceability


router = APIRouter(prefix="/projects/{project_id}", tags=["Traceability & Impact"], dependencies=[Depends(require_pro)])


SNAPSHOT_START = "\n--- SYSTEM TRACEABILITY SNAPSHOT START ---\n"
SNAPSHOT_END = "\n--- SYSTEM TRACEABILITY SNAPSHOT END ---\n"


def _upsert_snapshot(existing: str, snapshot: str) -> str:
    """
    Never overwrite user-entered content outside the snapshot markers.
    If markers exist, replace only the snapshot section.
    Otherwise, append a snapshot section to the end.
    """
    base = existing or ""
    if SNAPSHOT_START in base and SNAPSHOT_END in base:
        pre = base.split(SNAPSHOT_START, 1)[0]
        post = base.split(SNAPSHOT_END, 1)[1]
        return pre.rstrip() + SNAPSHOT_START + (snapshot or "").strip() + SNAPSHOT_END + post.lstrip()
    # append
    if base.strip():
        return base.rstrip() + "\n" + SNAPSHOT_START + (snapshot or "").strip() + SNAPSHOT_END
    return SNAPSHOT_START + (snapshot or "").strip() + SNAPSHOT_END


@router.post("/traceability/rebuild", status_code=status.HTTP_200_OK)
def rebuild_traceability(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Rebuild the Traceability Matrix snapshot (deterministic).
    - Enforces project ownership
    - Does NOT overwrite user content (stores/refreshes a system snapshot section)
    - Creates a new document version via update_document when content changes
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc = document_crud.get_document_by_type(db, project_id=project_id, doc_type="traceability_matrix")
    if not doc:
        raise HTTPException(status_code=404, detail="Traceability Matrix document not found")

    snapshot, stats = build_traceability(db, project_id=project_id)
    new_content = _upsert_snapshot(doc.content or "", snapshot)
    updated = document_crud.update_document(db, doc.id, DocumentUpdate(content=new_content, status="draft"), project_id)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update traceability matrix")

    return {"project_id": project_id, "doc_id": doc.id, "stats": stats}

