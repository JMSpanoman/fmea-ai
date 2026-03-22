from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import capa as capa_schemas
from crud import capa as capa_crud
from crud import project as project_crud
from services.capa_workflow_service import CapaWorkflowError
from services.capa_ai_prompts import list_ai_hook_prompts
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["CAPA Phase 2"], dependencies=[Depends(require_pro)])


@router.get("/capas/_meta/ai-review-hooks")
def capa_ai_review_hooks_meta():
    """Placeholder prompts for AI-assisted review (never auto-closes CAPA)."""
    return {"hooks": list_ai_hook_prompts()}


def _project_or_404(db: Session, project_id: str, user_id: str):
    project = project_crud.get_project(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/capas", response_model=List[capa_schemas.CAPAOut])
def get_capas(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CAPAs for a project."""
    _project_or_404(db, project_id, current_user.id)
    return capa_crud.get_capas_by_project(db, project_id)


@router.post("/capas", response_model=capa_schemas.CAPAFullOut, status_code=status.HTTP_201_CREATED)
def create_capa(
    project_id: str,
    capa: capa_schemas.CAPACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new CAPA with enterprise workflow payload defaults."""
    _project_or_404(db, project_id, current_user.id)

    if hasattr(capa, "model_copy"):
        capa = capa.model_copy(update={"project_id": project_id})
    else:
        capa_dict = capa.dict() if hasattr(capa, "dict") else capa.model_dump()
        capa_dict["project_id"] = project_id
        capa = capa_schemas.CAPACreate(**capa_dict)

    row = capa_crud.create_capa(db, capa)
    return capa_crud.capa_to_full_out(db, row)


@router.get("/capas/{capa_id}", response_model=capa_schemas.CAPAFullOut)
def get_capa(
    project_id: str,
    capa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get CAPA with workflow payload and evidence records."""
    _project_or_404(db, project_id, current_user.id)

    capa = capa_crud.get_capa(db, capa_id, project_id)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")

    return capa_crud.capa_to_full_out(db, capa)


@router.put("/capas/{capa_id}", response_model=capa_schemas.CAPAFullOut)
def put_capa(
    project_id: str,
    capa_id: str,
    body: capa_schemas.CAPAUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update CAPA payload and workflow state (validated gates)."""
    _project_or_404(db, project_id, current_user.id)

    try:
        row = capa_crud.update_capa(db, capa_id, body, project_id, strict_validation=True)
    except CapaWorkflowError as e:
        raise HTTPException(status_code=422, detail={"message": e.message, "code": e.code})
    except ValidationError as e:
        raise HTTPException(status_code=422, detail={"message": str(e), "code": "validation_error"})

    if not row:
        raise HTTPException(status_code=404, detail="CAPA not found")

    return capa_crud.capa_to_full_out(db, row)


@router.delete("/capas/{capa_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_capa(
    project_id: str,
    capa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _project_or_404(db, project_id, current_user.id)
    ok = capa_crud.delete_capa(db, capa_id, project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return None


@router.post(
    "/capas/{capa_id}/evidences",
    response_model=capa_schemas.CAPAEvidenceOut,
    status_code=status.HTTP_201_CREATED,
)
def add_capa_evidence(
    project_id: str,
    capa_id: str,
    body: capa_schemas.CAPAEvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach objective evidence to a CAPA (required before effectiveness confirmation)."""
    _project_or_404(db, project_id, current_user.id)
    ev = capa_crud.add_evidence(db, capa_id, project_id, body)
    if not ev:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return ev


@router.delete("/capas/{capa_id}/evidences/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_capa_evidence(
    project_id: str,
    capa_id: str,
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _project_or_404(db, project_id, current_user.id)
    ok = capa_crud.delete_evidence(db, capa_id, project_id, evidence_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Evidence or CAPA not found")
    return None

