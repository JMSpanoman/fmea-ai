from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from crud import project as project_crud
from services.project_setup_initializer import initialize_project_content
from services.project_profile_initializer import initialize_project_from_profile
from services.project_ai_doc_generator import generate_all_docs_with_ai_from_setup
from pydantic import BaseModel
from typing import Optional, List


router = APIRouter(prefix="/projects/{project_id}", tags=["Project Initialize"], dependencies=[Depends(require_pro)])


@router.post("/initialize", status_code=status.HTTP_200_OK)
def initialize_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Idempotent post-wizard initializer:
    - Ensures required documents exist
    - Seeds Hazard Analysis inputs (Risk Items) if empty
    - Seeds FMEA rows if empty
    - Optionally generates Hazard Analysis document HTML if empty/starter
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = initialize_project_content(db, project_id=project_id, user_id=current_user.id)
    return {"project_id": project_id, "stats": stats}


@router.post("/initialize-from-profile", status_code=status.HTTP_200_OK)
def initialize_project_from_profile_endpoint(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Controlled initializer:
    - Drafts select documents from ProjectProfile + Components
    - Idempotent; does not overwrite non-empty document content
    - Creates a new document version when content is generated
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = initialize_project_from_profile(db, project_id=project_id)
    return {"project_id": project_id, "stats": stats}


class GenerateAIDraftsFromSetupRequest(BaseModel):
    doc_types: Optional[List[str]] = None


@router.post("/generate-ai-drafts-from-setup", status_code=status.HTTP_200_OK)
def generate_ai_drafts_from_setup_endpoint(
    project_id: str,
    request: GenerateAIDraftsFromSetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate detailed AI drafts using Project Setup (ProjectProfile + Components).

    Audit-safe rules:
    - Never overwrite user-edited content
    - Only fills empty/not-started/starter content or exact deterministic setup scaffolds
    - Writes Draft content via document update (creates a new document version)
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        stats = generate_all_docs_with_ai_from_setup(
            db,
            project_id=project_id,
            doc_types=request.doc_types,
        )
        return {"project_id": project_id, "stats": stats}
    except RuntimeError as e:
        # e.g. OPENAI_API_KEY missing
        raise HTTPException(status_code=503, detail=str(e))

