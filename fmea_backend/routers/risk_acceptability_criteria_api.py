"""
API for Risk Acceptability Criteria report and configuration.
GET/POST report generation; GET/PATCH org config and project overrides.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
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
    SOURCE_USER_EDITED,
    SOURCE_SYSTEM_DEFAULT,
    _apply_sections_to_report,
)
from services.risk_acceptability_defaults import DEFAULT_ALARP_TERMINOLOGY
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
    terminology_overrides: Optional[Dict[str, str]] = None
    severity_rationale: Optional[str] = None
    probability_rationale: Optional[str] = None
    matrix_rationale: Optional[str] = None
    decision_rules_rationale: Optional[str] = None
    overall_residual_risk_methods: Optional[List[str]] = None


class OrgConfigUpdate(BaseModel):
    severity_scale: Optional[List[Dict[str, Any]]] = None
    probability_scale: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[Dict[str, Any]] = None
    decision_rules: Optional[str] = None
    terminology_overrides: Optional[Dict[str, str]] = None
    template_name: Optional[str] = None
    severity_rationale: Optional[str] = None
    probability_rationale: Optional[str] = None
    matrix_rationale: Optional[str] = None
    decision_rules_rationale: Optional[str] = None
    overall_residual_risk_methods: Optional[List[str]] = None
    approval_policy: Optional[Dict[str, Any]] = None


class WorkflowStatusUpdate(BaseModel):
    status: str = Field(..., description="draft|in_review|pending_approval|approved|obsolete")
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class ReviewCommentCreate(BaseModel):
    section_key: str
    comment: str


class EditableDefaultsUpdate(BaseModel):
    decision_rule_wording: Optional[str] = None
    alarp_terminology: Optional[str] = None
    severity_rationale: Optional[str] = None
    probability_rationale: Optional[str] = None
    matrix_rationale: Optional[str] = None
    decision_rules_rationale: Optional[str] = None
    reset_to_default: Optional[List[str]] = None


class SectionUpdateRequest(BaseModel):
    value: Any
    last_edited_by: Optional[str] = None


class SectionApprovalRequest(BaseModel):
    approved: bool = True


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
    regenerate_using_defaults: bool = Query(False, description="Replace editable defaults with hardcoded defaults"),
    force_regenerate: bool = Query(False, description="Reset all sections to generated defaults"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new version of the Risk Acceptability Criteria report and persist it. Also updates the project document of type risk_acceptability_criteria if it exists."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    latest = (
        db.query(RiskAcceptabilityCriteria)
        .filter(RiskAcceptabilityCriteria.project_id == project_id)
        .order_by(RiskAcceptabilityCriteria.generated_at.desc())
        .first()
    )
    existing_report = json.loads(latest.content_json) if latest and latest.content_json else None

    report = build_report(
        db,
        project_id=project_id,
        project_name=project.name,
        profile=profile,
        generated_by=str(current_user.id),
        include_ai_narrative=use_ai,
        existing_report=existing_report,
        regenerate_using_defaults=regenerate_using_defaults or force_regenerate,
    )
    html = render_risk_acceptability_criteria_html(report)
    next_version = (latest.version + 1) if latest else 1
    rac = RiskAcceptabilityCriteria(
        project_id=project_id,
        version=next_version,
        status="draft",
        title=f"Risk Acceptability Criteria — {project.name}",
        content_json=json.dumps(report, default=str),
        sections_json=json.dumps(report.get("sections", {}), default=str),
        content_html=html,
        source_metadata=report.get("source_metadata"),
        section_metadata=report.get("section_metadata"),
        readiness_metrics=report.get("readiness"),
        section_document_version=int((report.get("document_header", {}) or {}).get("section_document_version", next_version)),
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


def _create_report_snapshot(
    db: Session,
    *,
    project_id: str,
    project_name: str,
    current_user: User,
    base_rac: RiskAcceptabilityCriteria,
    report: Dict[str, Any],
) -> RiskAcceptabilityCriteria:
    latest = (
        db.query(RiskAcceptabilityCriteria)
        .filter(RiskAcceptabilityCriteria.project_id == project_id)
        .order_by(RiskAcceptabilityCriteria.generated_at.desc())
        .first()
    )
    next_version = (latest.version + 1) if latest else 1
    report.setdefault("document_header", {})
    report["document_header"]["version"] = next_version
    report["document_header"]["section_document_version"] = int(report["document_header"].get("section_document_version", 0) or 0) + 1
    _apply_sections_to_report(report, report.get("sections", {}))
    html = render_risk_acceptability_criteria_html(report)
    new_rac = RiskAcceptabilityCriteria(
        project_id=project_id,
        version=next_version,
        status="draft",
        title=f"Risk Acceptability Criteria — {project_name}",
        content_json=json.dumps(report, default=str),
        sections_json=json.dumps(report.get("sections", {}), default=str),
        content_html=html,
        source_metadata=report.get("source_metadata"),
        section_metadata=report.get("section_metadata"),
        readiness_metrics=report.get("readiness"),
        generated_by=str(current_user.id),
        supersedes_id=base_rac.id,
        section_document_version=report["document_header"]["section_document_version"],
    )
    db.add(new_rac)
    db.commit()
    db.refresh(new_rac)
    return new_rac


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
            "terminology_overrides": override.terminology_overrides,
            "severity_rationale": override.severity_rationale,
            "probability_rationale": override.probability_rationale,
            "matrix_rationale": override.matrix_rationale,
            "decision_rules_rationale": override.decision_rules_rationale,
            "overall_residual_risk_methods": override.overall_residual_risk_methods,
            "workflow_state": override.workflow_state,
            "approved_by": override.approved_by,
            "approved_at": override.approved_at.isoformat() if override.approved_at else None,
        }
    }


@router.patch("/risk-acceptability-criteria/override")
def update_project_criteria_override(
  project_id: str,
  body: ProjectOverrideUpdate,
  create_new_if_locked: bool = Query(True, description="When override is approved, create new draft row"),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
    """Create or update project-specific criteria override. Does not set approved_by/approved_at; use approve endpoint for that."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    override = get_project_override(db, project_id)
    if override and override.workflow_state == "approved":
        if not create_new_if_locked:
            raise HTTPException(status_code=409, detail="Approved override is read-only. Create a new draft version.")
        new_override = ProjectRiskCriteriaOverride(
            project_id=project_id,
            severity_scale=override.severity_scale,
            probability_scale=override.probability_scale,
            risk_matrix=override.risk_matrix,
            decision_rules=override.decision_rules,
            terminology_overrides=override.terminology_overrides,
            severity_rationale=override.severity_rationale,
            probability_rationale=override.probability_rationale,
            matrix_rationale=override.matrix_rationale,
            decision_rules_rationale=override.decision_rules_rationale,
            overall_residual_risk_methods=override.overall_residual_risk_methods,
            workflow_state="draft",
        )
        db.add(new_override)
        db.flush()
        override = new_override
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
    if body.terminology_overrides is not None:
        override.terminology_overrides = body.terminology_overrides
    if body.severity_rationale is not None:
        override.severity_rationale = body.severity_rationale
    if body.probability_rationale is not None:
        override.probability_rationale = body.probability_rationale
    if body.matrix_rationale is not None:
        override.matrix_rationale = body.matrix_rationale
    if body.decision_rules_rationale is not None:
        override.decision_rules_rationale = body.decision_rules_rationale
    if body.overall_residual_risk_methods is not None:
        override.overall_residual_risk_methods = body.overall_residual_risk_methods
    override.workflow_state = "draft"
    override.approved_at = None
    override.approved_by = None
    override.rejection_reason = None
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
            "template_name": config.template_name,
            "severity_rationale": config.severity_rationale,
            "probability_rationale": config.probability_rationale,
            "matrix_rationale": config.matrix_rationale,
            "decision_rules_rationale": config.decision_rules_rationale,
            "overall_residual_risk_methods": config.overall_residual_risk_methods,
            "approval_policy": config.approval_policy,
            "is_approved": config.is_approved,
            "approved_by": config.approved_by,
            "approved_at": config.approved_at.isoformat() if config.approved_at else None,
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
    if body.template_name is not None:
        config.template_name = body.template_name
    if body.severity_rationale is not None:
        config.severity_rationale = body.severity_rationale
    if body.probability_rationale is not None:
        config.probability_rationale = body.probability_rationale
    if body.matrix_rationale is not None:
        config.matrix_rationale = body.matrix_rationale
    if body.decision_rules_rationale is not None:
        config.decision_rules_rationale = body.decision_rules_rationale
    if body.overall_residual_risk_methods is not None:
        config.overall_residual_risk_methods = body.overall_residual_risk_methods
    if body.approval_policy is not None:
        config.approval_policy = body.approval_policy
    db.commit()
    db.refresh(config)
    return {"id": config.id, "name": config.name}


@router.post("/risk-acceptability-criteria/reports/{report_id}/status")
def update_risk_acceptability_status(
    project_id: str,
    report_id: str,
    body: WorkflowStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    allowed = {"draft", "in_review", "pending_approval", "approved", "obsolete"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")
    if rac.status == "approved" and body.status == "draft":
        raise HTTPException(status_code=409, detail="Approved version is immutable; generate new version")
    rac.status = body.status
    if body.status == "approved":
        rac.approved_by = str(current_user.id)
        rac.approved_at = datetime.now(timezone.utc)
    if body.approval_notes is not None:
        rac.approval_notes = body.approval_notes
    if body.rejection_reason is not None:
        rac.rejection_reason = body.rejection_reason
    db.commit()
    return {"id": rac.id, "status": rac.status}


@router.post("/risk-acceptability-criteria/reports/{report_id}/comments")
def add_review_comment(
    project_id: str,
    report_id: str,
    body: ReviewCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    comments = rac.review_comments or {}
    section_comments = comments.get(body.section_key, [])
    section_comments.append({
        "comment": body.comment,
        "author_id": str(current_user.id),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    comments[body.section_key] = section_comments
    rac.review_comments = comments
    db.commit()
    return {"ok": True, "comments": comments.get(body.section_key, [])}


@router.patch("/risk-acceptability-criteria/reports/{report_id}/editable-defaults")
def update_editable_defaults(
    project_id: str,
    report_id: str,
    body: EditableDefaultsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    report = json.loads(rac.content_json) if rac.content_json else {}
    editable = report.get("editable_defaults", {})
    now_iso = datetime.now(timezone.utc).isoformat()

    updates = {
        "decision_rule_wording": body.decision_rule_wording,
        "alarp_terminology": body.alarp_terminology,
        "severity_rationale": body.severity_rationale,
        "probability_rationale": body.probability_rationale,
        "matrix_rationale": body.matrix_rationale,
        "decision_rules_rationale": body.decision_rules_rationale,
    }
    reset_fields = set(body.reset_to_default or [])
    for key, val in updates.items():
        if key not in editable:
            continue
        if key in reset_fields:
            editable[key]["current_value"] = editable[key].get("default_value")
            editable[key]["source_type"] = "system_default"
            editable[key]["requires_human_review"] = True
            editable[key]["last_edited_by"] = str(current_user.id)
            editable[key]["last_edited_at"] = now_iso
            continue
        if val is not None:
            editable[key]["current_value"] = val
            editable[key]["source_type"] = SOURCE_USER_EDITED
            editable[key]["requires_human_review"] = False
            editable[key]["last_edited_by"] = str(current_user.id)
            editable[key]["last_edited_at"] = now_iso

    report["editable_defaults"] = editable
    selected_alarp = editable.get("alarp_terminology", {}).get("current_value") or DEFAULT_ALARP_TERMINOLOGY

    def _apply_alarp_terminology(text: str) -> str:
        if not text:
            return text
        updated = text.replace("Acceptable with Justification (ALARP)", selected_alarp)
        updated = updated.replace("\"ALARP\"", f"\"{selected_alarp}\"")
        updated = updated.replace(" (ALARP)", f" ({selected_alarp})")
        return updated

    # Reflect in rendered sections
    report.setdefault("decision_rules", {})["text"] = _apply_alarp_terminology(editable.get("decision_rule_wording", {}).get("current_value"))
    report.setdefault("decision_rules", {})["rationale"] = _apply_alarp_terminology(editable.get("decision_rules_rationale", {}).get("current_value"))
    report.setdefault("severity_scale", {})["rationale"] = editable.get("severity_rationale", {}).get("current_value")
    report.setdefault("probability_scale", {})["rationale"] = editable.get("probability_rationale", {}).get("current_value")
    report.setdefault("risk_matrix", {})["rationale"] = _apply_alarp_terminology(editable.get("matrix_rationale", {}).get("current_value"))
    report.setdefault("terminology", {})["overrides"] = {"ALARP": selected_alarp}
    report["severity_rationale"] = {"text": editable.get("severity_rationale", {}).get("current_value"), "source_type": editable.get("severity_rationale", {}).get("source_type")}
    report["probability_rationale"] = {"text": editable.get("probability_rationale", {}).get("current_value"), "source_type": editable.get("probability_rationale", {}).get("source_type")}
    report["alarp_terminology"] = {"text": selected_alarp, "source_type": editable.get("alarp_terminology", {}).get("source_type")}
    report["matrix_rationale"] = {"text": report.get("risk_matrix", {}).get("rationale"), "source_type": editable.get("matrix_rationale", {}).get("source_type")}
    report["decision_rule_wording"] = {"text": report.get("decision_rules", {}).get("text"), "source_type": editable.get("decision_rule_wording", {}).get("source_type")}
    report["decision_rules_rationale"] = {"text": report.get("decision_rules", {}).get("rationale"), "source_type": editable.get("decision_rules_rationale", {}).get("source_type")}
    report.setdefault("residual_risk_rules", {})["text"] = (
        "• Residual risk is evaluated after implementation of risk controls.\n"
        "• When residual risk falls within \"Acceptable\" per the risk matrix, no further action is required beyond documentation.\n"
        f"• When residual risk remains in \"{selected_alarp}\", documented justification and review are required.\n"
        "• When residual risk remains \"Unacceptable\", escalation to benefit-risk analysis is required before acceptance."
    )

    rac.content_json = json.dumps(report, default=str)
    rac.content_html = render_risk_acceptability_criteria_html(report)
    db.commit()
    db.refresh(rac)
    return {"id": rac.id, "editable_defaults": editable}


@router.patch("/risk-acceptability-criteria/reports/{report_id}/sections/{section_key}")
def update_report_section(
    project_id: str,
    report_id: str,
    section_key: str,
    body: SectionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    report = json.loads(rac.content_json) if rac.content_json else {}
    sections = report.get("sections") or (json.loads(rac.sections_json) if rac.sections_json else {})
    if section_key not in sections:
        raise HTTPException(status_code=404, detail="Section not found")
    section = sections[section_key]
    now_iso = datetime.now(timezone.utc).isoformat()
    history = section.get("history", []) or []
    history.append(
        {
            "version": int(section.get("version", 1) or 1),
            "value": section.get("value"),
            "changed_at": now_iso,
            "changed_by": str(current_user.id),
        }
    )
    section["value"] = body.value
    section["is_user_edited"] = True
    section["source_type"] = SOURCE_USER_EDITED
    section["last_edited_by"] = body.last_edited_by or str(current_user.id)
    section["last_edited_at"] = now_iso
    section["version"] = int(section.get("version", 1) or 1) + 1
    section["history"] = history
    section["approved"] = False
    sections[section_key] = section
    report["sections"] = sections
    new_rac = _create_report_snapshot(
        db,
        project_id=project_id,
        project_name=project.name,
        current_user=current_user,
        base_rac=rac,
        report=report,
    )
    return {"id": new_rac.id, "version": new_rac.version, "section": sections[section_key]}


@router.post("/risk-acceptability-criteria/reports/{report_id}/sections/{section_key}/approve")
def approve_report_section(
    project_id: str,
    report_id: str,
    section_key: str,
    body: SectionApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    report = json.loads(rac.content_json) if rac.content_json else {}
    sections = report.get("sections") or (json.loads(rac.sections_json) if rac.sections_json else {})
    if section_key not in sections:
        raise HTTPException(status_code=404, detail="Section not found")
    section = sections[section_key]
    section["approved"] = bool(body.approved)
    section["last_edited_by"] = str(current_user.id)
    section["last_edited_at"] = datetime.now(timezone.utc).isoformat()
    sections[section_key] = section
    report["sections"] = sections
    new_rac = _create_report_snapshot(
        db,
        project_id=project_id,
        project_name=project.name,
        current_user=current_user,
        base_rac=rac,
        report=report,
    )
    return {"id": new_rac.id, "version": new_rac.version, "section": sections[section_key]}


@router.post("/risk-acceptability-criteria/reports/{report_id}/approve-all-sections")
def approve_all_report_sections(
    project_id: str,
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    report = json.loads(rac.content_json) if rac.content_json else {}
    sections = report.get("sections") or (json.loads(rac.sections_json) if rac.sections_json else {})
    now_iso = datetime.now(timezone.utc).isoformat()
    for key in sections.keys():
        sections[key]["approved"] = True
        sections[key]["last_edited_by"] = str(current_user.id)
        sections[key]["last_edited_at"] = now_iso
    report["sections"] = sections
    new_rac = _create_report_snapshot(
        db,
        project_id=project_id,
        project_name=project.name,
        current_user=current_user,
        base_rac=rac,
        report=report,
    )
    return {"id": new_rac.id, "version": new_rac.version, "approved_sections": list(sections.keys())}


@router.post("/risk-acceptability-criteria/reports/{report_id}/sections/{section_key}/reset-default")
def reset_report_section_to_default(
    project_id: str,
    report_id: str,
    section_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    rac = db.query(RiskAcceptabilityCriteria).filter(
        RiskAcceptabilityCriteria.id == report_id,
        RiskAcceptabilityCriteria.project_id == project_id,
    ).first()
    if not rac:
        raise HTTPException(status_code=404, detail="Report not found")
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    regenerated = build_report(
        db,
        project_id=project_id,
        project_name=project.name,
        profile=profile,
        generated_by=str(current_user.id),
        existing_report={},
        regenerate_using_defaults=True,
    )
    default_sections = regenerated.get("sections", {})
    if section_key not in default_sections:
        raise HTTPException(status_code=404, detail="Section not found")
    report = json.loads(rac.content_json) if rac.content_json else {}
    sections = report.get("sections") or (json.loads(rac.sections_json) if rac.sections_json else {})
    sections[section_key] = default_sections[section_key]
    sections[section_key]["source_type"] = SOURCE_SYSTEM_DEFAULT
    sections[section_key]["is_user_edited"] = False
    sections[section_key]["approved"] = False
    sections[section_key]["last_edited_by"] = str(current_user.id)
    sections[section_key]["last_edited_at"] = datetime.now(timezone.utc).isoformat()
    report["sections"] = sections
    new_rac = _create_report_snapshot(
        db,
        project_id=project_id,
        project_name=project.name,
        current_user=current_user,
        base_rac=rac,
        report=report,
    )
    return {"id": new_rac.id, "version": new_rac.version, "section": sections[section_key]}


@router.post("/risk-acceptability-criteria/override/reset")
def reset_override_to_org_default(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    override = get_project_override(db, project_id)
    if override:
        db.delete(override)
        db.commit()
    return {"ok": True}


@router.post("/risk-acceptability-criteria/override/clone-from-project/{source_project_id}")
def clone_override_from_project(
    project_id: str,
    source_project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = project_crud.get_project(db, project_id, current_user.id)
    source = project_crud.get_project(db, source_project_id, current_user.id)
    if not target or not source:
        raise HTTPException(status_code=404, detail="Project not found")
    src_override = get_project_override(db, source_project_id)
    if not src_override:
        raise HTTPException(status_code=404, detail="Source project has no override")
    new_override = ProjectRiskCriteriaOverride(
        project_id=project_id,
        severity_scale=src_override.severity_scale,
        probability_scale=src_override.probability_scale,
        risk_matrix=src_override.risk_matrix,
        decision_rules=src_override.decision_rules,
        terminology_overrides=src_override.terminology_overrides,
        severity_rationale=src_override.severity_rationale,
        probability_rationale=src_override.probability_rationale,
        matrix_rationale=src_override.matrix_rationale,
        decision_rules_rationale=src_override.decision_rules_rationale,
        overall_residual_risk_methods=src_override.overall_residual_risk_methods,
        workflow_state="draft",
    )
    db.add(new_override)
    db.commit()
    db.refresh(new_override)
    return {"id": new_override.id}


@router.get("/risk-acceptability-criteria/compare-org-default")
def compare_project_with_org_default(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    override = get_project_override(db, project_id)
    org = get_org_config(db)
    return {
        "project_override": {
            "severity_scale": getattr(override, "severity_scale", None),
            "probability_scale": getattr(override, "probability_scale", None),
            "risk_matrix": getattr(override, "risk_matrix", None),
            "decision_rules": getattr(override, "decision_rules", None),
            "terminology_overrides": getattr(override, "terminology_overrides", None),
        },
        "org_default": {
            "severity_scale": getattr(org, "severity_scale", None),
            "probability_scale": getattr(org, "probability_scale", None),
            "risk_matrix": getattr(org, "risk_matrix", None),
            "decision_rules": getattr(org, "decision_rules", None),
            "terminology_overrides": getattr(org, "terminology_overrides", None),
        },
    }
