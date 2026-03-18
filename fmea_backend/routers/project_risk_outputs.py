"""
Phase 4: Structured risk outputs from project_risk_items.

GET endpoints for FMEA table, Hazard Analysis, Risk Analysis,
Risk Control Traceability, Verification Traceability, Residual Risk Evaluation,
and draft Risk Management Report sections.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from crud import project as project_crud
from services import project_risk_outputs_service as outputs

router = APIRouter(
    prefix="/projects/{project_id}/risk-outputs",
    tags=["Project Risk Outputs (Phase 4)"],
    dependencies=[Depends(require_pro)],
)


def _ensure_project(db: Session, project_id: str, user_id: str) -> None:
    from fastapi import HTTPException
    if not project_crud.get_project(db, project_id, user_id):
        raise HTTPException(status_code=404, detail="Project not found")


@router.get("/fmea-table")
def get_fmea_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """FMEA-style table generated from project risk items (component, failure mode, hazard, S/P/D, controls, residual)."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_fmea_table(db, project_id)}


@router.get("/hazard-analysis-table")
def get_hazard_analysis_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Hazard analysis table: hazard, hazardous situation, harm, device/component."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_hazard_analysis_table(db, project_id)}


@router.get("/risk-analysis-table")
def get_risk_analysis_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Risk analysis table: hazard, harm, severity, probability, detectability, risk score, acceptability."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_risk_analysis_table(db, project_id)}


@router.get("/risk-control-traceability-table")
def get_risk_control_traceability_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Risk control traceability: risk item → control → implementation reference."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_risk_control_traceability_table(db, project_id)}


@router.get("/verification-traceability-table")
def get_verification_traceability_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verification traceability: control → verification → evidence, status."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_verification_traceability_table(db, project_id)}


@router.get("/residual-risk-evaluation-table")
def get_residual_risk_evaluation_table(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Residual risk evaluation table: inherent vs residual S, P, D, score, acceptability."""
    _ensure_project(db, project_id, current_user.id)
    return {"rows": outputs.build_residual_risk_evaluation_table(db, project_id)}


@router.get("/risk-management-report-draft")
def get_risk_management_report_draft(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Draft Risk Management Report sections (intro, hazard, risk, controls, verification, residual, traceability)."""
    _ensure_project(db, project_id, current_user.id)
    return outputs.build_risk_management_report_draft(db, project_id)
