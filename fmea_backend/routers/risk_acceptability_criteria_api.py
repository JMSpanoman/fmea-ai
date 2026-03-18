"""
API for Risk Acceptability Criteria report and configuration.
GET/POST report generation; GET/PATCH org config and project overrides.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.plan import require_pro
from database import get_db
from models.user import User
from crud import project as project_crud

from services.risk_acceptability_criteria_service import (
    build_report,
    get_merged_criteria,
    get_org_config,
    get_project_override,
)
from business_logic.risk_acceptability_criteria_renderer import render_risk_acceptability_criteria_html
from models.risk_acceptability_criteria import (
    RiskAcceptabilityCriteria,
    OrganizationRiskCriteriaConfig,
    ProjectRiskCriteriaOverride,
)
from models.project_profile import ProjectProfile


router = APIRouter(
    prefix="/projects/{project_id}",
    tags=["Risk Acceptability Criteria"],
    dependencies=[Depends(require_pro)],
)

# Org-level config (no project_id)
router_org = APIRouter(
    prefix="/risk-acceptability-criteria",
    tags=["Risk Acceptability Criteria (Org)"],
    dependencies=[Depends(require_pro)],
)


# --- Schemas ---
class RiskAcceptabilityReportResponse(BaseModel):
    id: Optional[str] = None
    project_id: str
    version: int
    status: str
    title: Optional[str] = None
    report: Dict[str, Any]
    rendered_html: Optional[str] = None
    generated_at: Optional[str] = None


class ProjectOverrideUpdate(BaseModel):
    severity_scale: Optional[List[Dict[str, Any]]] = None
    probability_scale: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[Dict[str, Any]] = None
    decision_rules: Optional[str] = None


class OrgConfigUpdate(BaseModel):
    severity_scale: Optional[List[Dict[str, Any]]] = None
    probability_scale: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[Dict[str, Any]] = None
    decision_rules: Optional[str] = None
    terminology_overrides: Optional[Dict[str, str]] = None


# --- Report ---
@router.get("/risk-acceptability-criteria/report", response_model=RiskAcceptabilityReportResponse)
def get_risk_acceptability_report(
    project_id: str,
    version: Optional[int] = Query(None, description="Specific version; omit for latest"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the latest or specified version of the Risk Acceptability Criteria report (JSON + optional HTML)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if version is not None:
        rac = (
            db.query(RiskAcceptabilityCriteria)
            .filter(
                RiskAcceptabilityCriteria.project_id == project_id,
                RiskAcceptabilityCriteria.version == version,
            )
            .first()
        )
    else:
        rac = (
            db.query(RiskAcceptabilityCriteria)
            .filter(RiskAcceptabilityCriteria.project_id == project_id)
            .order_by(RiskAcceptabilityCriteria.generated_at.desc())
            .first()
        )

    if rac:
        report = json.loads(rac.content_json) if rac.content_json else {}
        return RiskAcceptabilityReportResponse(
            id=rac.id,
            project_id=rac.project_id,
            version=rac.version,
            status=rac.status,
            title=rac.title,
            report=report,
            rendered_html=rac.content_html,
            generated_at=rac.generated_at.isoformat() if rac.generated_at else None,
        )

    # No stored report: build on-the-fly (no persist)
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    report = build_report(db, project_id=project_id, project_name=project.name, profile=profile, generated_by=None)
    html = render_risk_acceptability_criteria_html(report)
    return RiskAcceptabilityReportResponse(
        project_id=project_id,
        version=0,
        status="draft",
        title=f"Risk Acceptability Criteria — {project.name}",
        report=report,
        rendered_html=html,
        generated_at=None,
    )


@router.post("/risk-acceptability-criteria/generate", response_model=RiskAcceptabilityReportResponse)
def generate_risk_acceptability_report(
    project_id: str,
    use_ai: bool = Query(False, description="Use AI for narrative sections"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new version of the Risk Acceptability Criteria report and persist it. Also updates the project document of type risk_acceptability_criteria if it exists."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    report = build_report(
        db,
        project_id=project_id,
        project_name=project.name,
        profile=profile,
        generated_by=str(current_user.id),
        include_ai_narrative=use_ai,
    )
    html = render_risk_acceptability_criteria_html(report)

    latest = (
        db.query(RiskAcceptabilityCriteria)
        .filter(RiskAcceptabilityCriteria.project_id == project_id)
        .order_by(RiskAcceptabilityCriteria.generated_at.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1
    rac = RiskAcceptabilityCriteria(
        project_id=project_id,
        version=next_version,
        status="draft",
        title=f"Risk Acceptability Criteria — {project.name}",
        content_json=json.dumps(report, default=str),
        content_html=html,
        source_metadata=report.get("source_metadata"),
        generated_by=str(current_user.id),
    )
    db.add(rac)
    db.commit()
    db.refresh(rac)

    return RiskAcceptabilityReportResponse(
        id=rac.id,
        project_id=rac.project_id,
        version=rac.version,
        status=rac.status,
        title=rac.title,
        report=report,
        rendered_html=rac.content_html,
        generated_at=rac.generated_at.isoformat() if rac.generated_at else None,
    )


# --- Merged criteria (for UI: show current effective criteria) ---
@router.get("/risk-acceptability-criteria/merged")
def get_merged_risk_acceptability_criteria(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return merged severity scale, probability scale, risk matrix, and decision rules (project override → org → system draft)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    merged, section_sources = get_merged_criteria(db, project_id)
    return {"criteria": merged, "source_metadata": section_sources}


# --- Project override ---
@router.get("/risk-acceptability-criteria/override")
def get_project_criteria_override(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project-specific approved override if any."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    override = get_project_override(db, project_id)
    if not override:
        return {"override": None}
    return {
        "override": {
            "id": override.id,
            "project_id": override.project_id,
            "severity_scale": override.severity_scale,
            "probability_scale": override.probability_scale,
            "risk_matrix": override.risk_matrix,
            "decision_rules": override.decision_rules,
            "approved_by": override.approved_by,
            "approved_at": override.approved_at.isoformat() if override.approved_at else None,
        }
    }


@router.patch("/risk-acceptability-criteria/override")
def update_project_criteria_override(
  project_id: str,
  body: ProjectOverrideUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
    """Create or update project-specific criteria override. Does not set approved_by/approved_at; use approve endpoint for that."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    override = get_project_override(db, project_id)
    if not override:
        override = ProjectRiskCriteriaOverride(project_id=project_id)
        db.add(override)
        db.flush()
    if body.severity_scale is not None:
        override.severity_scale = body.severity_scale
    if body.probability_scale is not None:
        override.probability_scale = body.probability_scale
    if body.risk_matrix is not None:
        override.risk_matrix = body.risk_matrix
    if body.decision_rules is not None:
        override.decision_rules = body.decision_rules
    db.commit()
    db.refresh(override)
    return {"id": override.id, "project_id": override.project_id}


# --- Organization config (global default; single row "default") ---
@router_org.get("/org-config")
def get_organization_criteria_config(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
    """Get organization-level default criteria config. Not project-scoped."""
    config = get_org_config(db)
    if not config:
        return {"config": None}
    return {
        "config": {
            "id": config.id,
            "name": config.name,
            "severity_scale": config.severity_scale,
            "probability_scale": config.probability_scale,
            "risk_matrix": config.risk_matrix,
            "decision_rules": config.decision_rules,
            "terminology_overrides": config.terminology_overrides,
        }
    }


@router_org.patch("/org-config")
def update_organization_criteria_config(
  body: OrgConfigUpdate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
    """Create or update organization default criteria (single 'default' row)."""
    config = get_org_config(db)
    if not config:
        config = OrganizationRiskCriteriaConfig(name="default")
        db.add(config)
        db.flush()
    if body.severity_scale is not None:
        config.severity_scale = body.severity_scale
    if body.probability_scale is not None:
        config.probability_scale = body.probability_scale
    if body.risk_matrix is not None:
        config.risk_matrix = body.risk_matrix
    if body.decision_rules is not None:
        config.decision_rules = body.decision_rules
    if body.terminology_overrides is not None:
        config.terminology_overrides = body.terminology_overrides
    db.commit()
    db.refresh(config)
    return {"id": config.id, "name": config.name}
