"""
Post-Market Surveillance (PMS) Plan Generator — FMEA + MAUDE-like signals + structured AI output.

Route order: literal paths (`/generate`, `/plan/...`) before `/{project_id}`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.plan import require_pro
from database import get_db
from models.user import User
from schemas.pms_plan import (
    PmsPlanGenerateRequest,
    PmsPlanGenerateResponse,
    PmsPlanHistoryItem,
    PmsPlanHistoryListResponse,
)
from services.pms_plan_generator_service import (
    build_pms_plan_printable_html,
    generate_pms_plan,
    get_pms_plan_for_user,
    get_pms_plan_history_item,
    list_pms_plans_for_project,
)

router = APIRouter(prefix="/pms", tags=["PMS Plan Generator"], dependencies=[Depends(require_pro)])


@router.post(
    "/generate",
    response_model=PmsPlanGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate PMS plan from FMEA + simulated MAUDE signals",
)
def post_generate_pms_plan(
    body: PmsPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Builds a structured PMS plan using project FMEA rows and MAUDE-like signals (simulated by default).
    Persists to `pms_generated_plans` and logs `ai_events` (context_type=`pms_plan`).
    """
    try:
        return generate_pms_plan(db, user_id=current_user.id, body=body)
    except PermissionError:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI output invalid: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"PMS plan generation failed: {e}")


@router.get(
    "/plan/{generation_id}/export/html",
    response_class=HTMLResponse,
    summary="Printable HTML export by generation id (browser Print → PDF)",
)
def export_pms_plan_html_by_id(
    generation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = get_pms_plan_for_user(db, user_id=current_user.id, generation_id=generation_id)
    if not item:
        raise HTTPException(status_code=404, detail="PMS plan not found")
    return HTMLResponse(content=build_pms_plan_printable_html(item=item))


@router.get(
    "/plan/{generation_id}",
    response_model=PmsPlanHistoryItem,
    summary="Get one saved PMS plan by generation id",
)
def get_pms_plan_by_generation_id(
    generation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = get_pms_plan_for_user(db, user_id=current_user.id, generation_id=generation_id)
    if not item:
        raise HTTPException(status_code=404, detail="PMS plan not found")
    return item


@router.get(
    "/{project_id}",
    response_model=PmsPlanHistoryListResponse,
    summary="List all PMS plans for a project (newest first)",
)
def list_pms_plans_for_project_route(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return list_pms_plans_for_project(db, user_id=current_user.id, project_id=project_id)
    except PermissionError:
        raise HTTPException(status_code=404, detail="Project not found or access denied")


# --- Legacy paths (project id in URL + generation id) ---


@router.get(
    "/plans/{project_id}/{generation_id}/export/html",
    response_class=HTMLResponse,
    summary="[Legacy] Printable HTML export with project id in path",
)
def export_pms_plan_html_legacy(
    project_id: str,
    generation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = get_pms_plan_history_item(
        db, user_id=current_user.id, project_id=project_id, generation_id=generation_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="PMS plan not found")
    return HTMLResponse(content=build_pms_plan_printable_html(item=item))


@router.get(
    "/plans/{project_id}/{generation_id}",
    response_model=PmsPlanHistoryItem,
    summary="[Legacy] Get one PMS plan with project id in path",
)
def get_pms_plan_by_project_and_id(
    project_id: str,
    generation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = get_pms_plan_history_item(
        db, user_id=current_user.id, project_id=project_id, generation_id=generation_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="PMS plan not found")
    return item


@router.get(
    "/plans/{project_id}",
    response_model=PmsPlanHistoryListResponse,
    summary="[Legacy] List PMS plans for a project",
)
def get_pms_plan_history_legacy(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return list_pms_plans_for_project(db, user_id=current_user.id, project_id=project_id)
    except PermissionError:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
