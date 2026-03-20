"""
Risk acceptability rule engine API — deterministic evaluation for FMEA rows.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.plan import require_pro
from crud import fmea as fmea_crud
from crud import project as project_crud
from crud import project_profile as project_profile_crud
from crud import project_risk_criteria as prc
from database import get_db
from models.component import Component
from models.user import User
from schemas import fmea as fmea_schemas
from schemas.project_risk_criteria import (
    GlobalResidualRiskSummaryOut,
    ProjectRiskCriteriaApprove,
    ProjectRiskCriteriaCreate,
    ProjectRiskCriteriaOut,
    ProjectRiskCriteriaUpdate,
    RuleEvaluationAuditOut,
    SeedRiskCriteriaRequest,
)
from services import risk_rule_engine as engine
from services.risk_rule_engine_defaults import build_default_criteria_payload
from services.risk_rule_evaluation_service import (
    apply_initial_evaluation,
    apply_residual_evaluation,
    evaluation_inputs_snapshot,
    resolve_criteria_for_evaluation,
)

router = APIRouter(tags=["Risk Rule Engine"], dependencies=[Depends(require_pro)])


def _get_project_or_404(db: Session, project_id: str, user_id: str):
    p = project_crud.get_project(db, project_id, user_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


def _component_name(db: Session, component_id: Optional[str]) -> str:
    if not component_id:
        return ""
    c = db.query(Component).filter(Component.id == component_id).first()
    return c.name if c else ""


# ---------------------------------------------------------------------------
# Project risk criteria (versioned)
# ---------------------------------------------------------------------------


@router.get("/projects/{project_id}/risk-criteria", response_model=List[ProjectRiskCriteriaOut])
def list_risk_criteria(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    rows = prc.list_criteria_for_project(db, project_id)
    return rows


@router.post(
    "/projects/{project_id}/risk-criteria",
    response_model=ProjectRiskCriteriaOut,
    status_code=status.HTTP_201_CREATED,
)
def create_risk_criteria(
    project_id: str,
    body: ProjectRiskCriteriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    return prc.create_criteria(db, project_id, body)


@router.post("/projects/{project_id}/risk-criteria/seed", response_model=ProjectRiskCriteriaOut)
def seed_risk_criteria(
    project_id: str,
    body: SeedRiskCriteriaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    if body.template not in ("iso14971_default_pacemaker", "iso14971_matrix_only"):
        raise HTTPException(status_code=400, detail="Unknown template")
    include_pm = body.template == "iso14971_default_pacemaker"
    payload = build_default_criteria_payload(
        evaluation_method="matrix",
        include_pacemaker_rules=include_pm,
    )
    create = ProjectRiskCriteriaCreate(**payload)
    return prc.create_criteria(db, project_id, create)


@router.put("/projects/{project_id}/risk-criteria/{criteria_id}", response_model=ProjectRiskCriteriaOut)
def update_risk_criteria(
    project_id: str,
    criteria_id: str,
    body: ProjectRiskCriteriaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    ent = prc.update_criteria(db, criteria_id, project_id, body)
    if not ent:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return ent


@router.post("/projects/{project_id}/risk-criteria/{criteria_id}/approve", response_model=ProjectRiskCriteriaOut)
def approve_risk_criteria(
    project_id: str,
    criteria_id: str,
    body: ProjectRiskCriteriaApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    ent = prc.get_criteria(db, criteria_id, project_id)
    if not ent:
        raise HTTPException(status_code=404, detail="Criteria not found")
    crit_dict = engine.criteria_entity_to_dict(ent)
    errors = engine.validate_criteria_config(crit_dict)
    if errors:
        raise HTTPException(
            status_code=400,
            detail={"message": "Criteria incomplete or invalid for approval", "errors": errors},
        )
    approved = prc.approve_criteria(db, criteria_id, project_id, body.approval_metadata)
    if not approved:
        raise HTTPException(status_code=404, detail="Criteria not found")
    return approved


# ---------------------------------------------------------------------------
# FMEA row evaluation
# ---------------------------------------------------------------------------


@router.post("/projects/{project_id}/fmea/{fmea_row_id}/evaluate-initial", response_model=fmea_schemas.FMEARowOut)
def evaluate_initial(
    project_id: str,
    fmea_row_id: str,
    criteria_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    row = fmea_crud.get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    crit, crit_dict = resolve_criteria_for_evaluation(db, project_id, criteria_id)
    if not crit or not crit_dict:
        raise HTTPException(status_code=400, detail="No risk criteria configured for this project")
    comp = _component_name(db, row.component_id)
    rdict = engine.row_to_dict(row)
    result = engine.evaluate_initial_risk(rdict, crit_dict, component_name=comp)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result)
    inputs = evaluation_inputs_snapshot(row, "initial")
    apply_initial_evaluation(db, row, crit.version, result, inputs)
    db.commit()
    db.refresh(row)
    return row


@router.post("/projects/{project_id}/fmea/{fmea_row_id}/evaluate-residual", response_model=fmea_schemas.FMEARowOut)
def evaluate_residual(
    project_id: str,
    fmea_row_id: str,
    criteria_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    row = fmea_crud.get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    crit, crit_dict = resolve_criteria_for_evaluation(db, project_id, criteria_id)
    if not crit or not crit_dict:
        raise HTTPException(status_code=400, detail="No risk criteria configured for this project")
    comp = _component_name(db, row.component_id)
    rdict = engine.row_to_dict(row)
    result = engine.evaluate_residual_risk(rdict, crit_dict, component_name=comp)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result)
    inputs = evaluation_inputs_snapshot(row, "residual")
    apply_residual_evaluation(db, row, crit.version, result, inputs)
    db.commit()
    db.refresh(row)
    return row


@router.post("/projects/{project_id}/fmea/{fmea_row_id}/re-evaluate", response_model=fmea_schemas.FMEARowOut)
def re_evaluate_row(
    project_id: str,
    fmea_row_id: str,
    criteria_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    row = fmea_crud.get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    crit, crit_dict = resolve_criteria_for_evaluation(db, project_id, criteria_id)
    if not crit or not crit_dict:
        raise HTTPException(status_code=400, detail="No risk criteria configured for this project")
    comp = _component_name(db, row.component_id)
    rdict = engine.row_to_dict(row)
    ri = engine.evaluate_initial_risk(rdict, crit_dict, component_name=comp)
    if not ri.get("ok"):
        raise HTTPException(status_code=400, detail={"phase": "initial", **ri})
    rr = engine.evaluate_residual_risk(rdict, crit_dict, component_name=comp)
    if not rr.get("ok"):
        raise HTTPException(status_code=400, detail={"phase": "residual", **rr})
    apply_initial_evaluation(db, row, crit.version, ri, evaluation_inputs_snapshot(row, "initial"))
    apply_residual_evaluation(db, row, crit.version, rr, evaluation_inputs_snapshot(row, "residual"))
    db.commit()
    db.refresh(row)
    return row


@router.get("/projects/{project_id}/fmea/{fmea_row_id}/rule-audit", response_model=List[RuleEvaluationAuditOut])
def list_rule_audit(
    project_id: str,
    fmea_row_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    row = fmea_crud.get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    from models.project_risk_criteria import RuleEvaluationAudit

    return (
        db.query(RuleEvaluationAudit)
        .filter(RuleEvaluationAudit.fmea_row_id == fmea_row_id, RuleEvaluationAudit.project_id == project_id)
        .order_by(RuleEvaluationAudit.created_at.desc())
        .all()
    )


@router.post("/projects/{project_id}/evaluate-all-risks")
def evaluate_all_risks(
    project_id: str,
    criteria_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    crit, crit_dict = resolve_criteria_for_evaluation(db, project_id, criteria_id)
    if not crit or not crit_dict:
        raise HTTPException(status_code=400, detail="No risk criteria configured for this project")
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    updated = 0
    errors: List[dict] = []
    for row in rows:
        comp = _component_name(db, row.component_id)
        rdict = engine.row_to_dict(row)
        ri = engine.evaluate_initial_risk(rdict, crit_dict, component_name=comp)
        rr = engine.evaluate_residual_risk(rdict, crit_dict, component_name=comp)
        if not ri.get("ok") or not rr.get("ok"):
            errors.append({"fmea_row_id": row.id, "initial": ri, "residual": rr})
            continue
        apply_initial_evaluation(db, row, crit.version, ri, evaluation_inputs_snapshot(row, "initial"))
        apply_residual_evaluation(db, row, crit.version, rr, evaluation_inputs_snapshot(row, "residual"))
        updated += 1
    db.commit()
    return {"updated_rows": updated, "errors": errors, "criteria_version": crit.version}


@router.get("/projects/{project_id}/global-residual-risk-summary", response_model=GlobalResidualRiskSummaryOut)
def global_residual_summary(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_project_or_404(db, project_id, current_user.id)
    crit = prc.get_latest_approved(db, project_id) or prc.get_latest_any(db, project_id)
    ver = crit.version if crit else 0
    # Without versioned criteria, only show counts — skip aggregate ISO gate (no special_rules source).
    crit_dict = (
        engine.criteria_entity_to_dict(crit)
        if crit
        else {"special_rules": {"global_residual_acceptability_policy": {"enabled": False}}}
    )
    prof = project_profile_crud.get_project_profile(db, project_id)
    attestations = None
    if prof is not None:
        attestations = {
            "overall_device_benefit_risk_profile_acceptable": prof.overall_device_benefit_risk_profile_acceptable,
            "rmr_overall_residual_risk_conclusion_documented": prof.rmr_overall_residual_risk_conclusion_documented,
        }
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    summary = engine.build_global_residual_summary(
        project_id=project_id,
        criteria_version=ver,
        rows=rows,
        top_n=15,
        criteria_dict=crit_dict,
        project_attestations=attestations,
    )
    return summary
