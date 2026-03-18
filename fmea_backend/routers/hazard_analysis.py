from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from models.project_profile import ProjectProfile
from crud import project as project_crud
from crud import hazard_analysis_item as ha_item_crud
from business_logic import hazard_analysis_builder, hazard_analysis_renderer
from business_logic.fmea_to_hazard_analysis import fmea_row_to_hazard_analysis_dict
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from schemas.hazard_analysis_item import (
    HazardAnalysisItemCreate,
    HazardAnalysisItemUpdate,
    HazardAnalysisItemResponse,
)

router = APIRouter(prefix="/projects/{project_id}", tags=["Hazard Analysis"], dependencies=[Depends(require_pro)])


def _project_profile_context(db: Session, project_id: str) -> tuple:
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    device_name = getattr(profile, "device_name", None) or getattr(profile, "device_description", None)
    intended_use = getattr(profile, "intended_use", None) if profile else None
    return (device_name, intended_use)


class ComponentFilter(BaseModel):
    id: Optional[str] = None
    name: str


class HazardAnalysisGenerateRequest(BaseModel):
    components: Optional[List[ComponentFilter]] = None
    version_scope: str = "approved_only"  # approved_only, current, all
    include_unapproved: bool = False
    include_metadata: bool = True
    include_ai_assist_summary: bool = False
    format: str = "html"


class HazardAnalysisEnrichRequest(BaseModel):
    max_items: int = 25
    only_if_missing: bool = True

@router.post("/hazard-analysis/enrich-ai", status_code=status.HTTP_200_OK)
def enrich_hazard_analysis_ai(
    project_id: str,
    request: HazardAnalysisEnrichRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enrich RiskItem current versions with AI-generated:
    - failure_mode
    - sequence_of_events

    Creates new immutable versions; does not overwrite prior versions.
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    from services.hazard_analysis_ai_enricher import enrich_hazard_analysis_fields

    stats = enrich_hazard_analysis_fields(
        db,
        project_id=project_id,
        user_id=current_user.id,
        max_items=request.max_items,
        only_if_missing=bool(request.only_if_missing),
    )
    return {"project_id": project_id, "stats": stats.as_dict()}

@router.post("/hazard-analysis/generate", status_code=status.HTTP_200_OK)
def generate_hazard_analysis(
    project_id: str,
    request: HazardAnalysisGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Hazard Analysis HTML report"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Build evidence
    component_filter = None
    if request.components:
        component_filter = [{"id": c.id, "name": c.name} for c in request.components]
    
    evidence = hazard_analysis_builder.build_hazard_analysis(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=request.version_scope,
        include_unapproved=request.include_unapproved,
    )
    device_name, intended_use = _project_profile_context(db, project_id)
    hazard_analysis_html = hazard_analysis_renderer.render_hazard_analysis_html(
        evidence, project.name, device_name=device_name, intended_use=intended_use
    )
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "version_scope": request.version_scope,
        "hazard_analysis_html": hazard_analysis_html,
        "counts": evidence.get("counts", {}),
    }

@router.get("/hazard-analysis/export", response_class=HTMLResponse)
def export_hazard_analysis(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    version_scope: str = Query("approved_only", description="Version scope: approved_only, current, all"),
    include_unapproved: bool = Query(False, description="Include unapproved versions"),
    format: str = Query("html", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export Hazard Analysis as HTML file"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse component filter
    component_filter = None
    if components:
        component_names = [name.strip() for name in components.split(",")]
        component_filter = [{"name": name} for name in component_names]
    
    evidence = hazard_analysis_builder.build_hazard_analysis(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=version_scope,
        include_unapproved=include_unapproved,
    )
    device_name, intended_use = _project_profile_context(db, project_id)
    hazard_analysis_html = hazard_analysis_renderer.render_hazard_analysis_html(
        evidence, project.name, device_name=device_name, intended_use=intended_use
    )
    return HTMLResponse(content=hazard_analysis_html)


# ---------- Hazard Analysis Items (full ISO 14971 schema) ----------


@router.get("/hazard-analysis/items", response_model=List[Dict[str, Any]])
def list_hazard_analysis_items(
    project_id: str,
    component_id: Optional[str] = Query(None),
    approval_status: Optional[str] = Query(None),
    hazard_category: Optional[str] = Query(None),
    include_draft: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hazard analysis items for the project (full schema)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    items = ha_item_crud.list_hazard_analysis_items(
        db, project_id=project_id, component_id=component_id,
        approval_status=approval_status, hazard_category=hazard_category,
        include_draft=include_draft,
    )
    out = []
    for d in items:
        row = {
            "id": d.id, "project_id": d.project_id, "component_id": d.component_id,
            "risk_key": d.risk_key, "version_no": d.version_no, "hazard_category": d.hazard_category,
            "hazard": d.hazard, "foreseeable_sequence_of_events": d.foreseeable_sequence_of_events,
            "hazardous_situation": d.hazardous_situation, "harm": d.harm, "affected_user": d.affected_user,
            "failure_mode": d.failure_mode, "cause_of_failure": d.cause_of_failure, "clinical_effect": d.clinical_effect,
            "operating_mode": d.operating_mode, "use_environment": d.use_environment,
            "initial_severity": d.initial_severity, "initial_probability": d.initial_probability,
            "initial_risk_level": d.initial_risk_level,
            "risk_control_measures": d.risk_control_measures, "risk_control_type": d.risk_control_type,
            "control_implementation_notes": d.control_implementation_notes,
            "residual_severity": d.residual_severity, "residual_probability": d.residual_probability,
            "residual_risk_level": d.residual_risk_level, "residual_risk_acceptability": d.residual_risk_acceptability,
            "related_design_input": d.related_design_input, "related_design_output": d.related_design_output,
            "verification_reference": d.verification_reference, "validation_reference": d.validation_reference,
            "requirement_ids": d.requirement_ids,
            "approval_status": d.approval_status, "approved_by": d.approved_by,
            "approved_at": d.approved_at.isoformat() if d.approved_at else None,
            "reviewer_comments": d.reviewer_comments,
            "ai_generated": d.ai_generated, "ai_confidence": d.ai_confidence, "source_context": d.source_context,
            "assumptions": d.assumptions,
            "component_name": d.component.name if d.component else None,
        }
        out.append(row)
    return out


@router.get("/hazard-analysis/items/{item_id}", response_model=Dict[str, Any])
def get_hazard_analysis_item(
    project_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    item = ha_item_crud.get_hazard_analysis_item(db, item_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Hazard analysis item not found")
    return {
        "id": item.id, "project_id": item.project_id, "component_id": item.component_id,
        "risk_key": item.risk_key, "version_no": item.version_no, "hazard_category": item.hazard_category,
        "hazard": item.hazard, "foreseeable_sequence_of_events": item.foreseeable_sequence_of_events,
        "hazardous_situation": item.hazardous_situation, "harm": item.harm, "affected_user": item.affected_user,
        "failure_mode": item.failure_mode, "cause_of_failure": item.cause_of_failure, "clinical_effect": item.clinical_effect,
        "operating_mode": item.operating_mode, "use_environment": item.use_environment,
        "initial_severity": item.initial_severity, "initial_probability": item.initial_probability,
        "initial_risk_level": item.initial_risk_level,
        "risk_control_measures": item.risk_control_measures, "risk_control_type": item.risk_control_type,
        "control_implementation_notes": item.control_implementation_notes,
        "residual_severity": item.residual_severity, "residual_probability": item.residual_probability,
        "residual_risk_level": item.residual_risk_level, "residual_risk_acceptability": item.residual_risk_acceptability,
        "related_design_input": item.related_design_input, "related_design_output": item.related_design_output,
        "verification_reference": item.verification_reference, "validation_reference": item.validation_reference,
        "requirement_ids": item.requirement_ids,
        "approval_status": item.approval_status, "approved_by": item.approved_by, "approved_at": item.approved_at.isoformat() if item.approved_at else None,
        "reviewer_comments": item.reviewer_comments,
        "ai_generated": item.ai_generated, "ai_confidence": item.ai_confidence, "source_context": item.source_context,
        "assumptions": item.assumptions,
        "component_name": item.component.name if item.component else None,
    }


@router.post("/hazard-analysis/items", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def create_hazard_analysis_item(
    project_id: str,
    payload: HazardAnalysisItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if str(payload.project_id) != str(project_id):
        raise HTTPException(status_code=400, detail="project_id mismatch")
    # Validation is enforced on approve; draft creation can have minimal fields for later AI fill
    item = ha_item_crud.create_hazard_analysis_item(db, payload, created_by=current_user.id)
    return {"id": item.id, "project_id": item.project_id, "risk_key": item.risk_key}


@router.patch("/hazard-analysis/items/{item_id}", response_model=Dict[str, Any])
def update_hazard_analysis_item(
    project_id: str,
    item_id: str,
    payload: HazardAnalysisItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    item = ha_item_crud.get_hazard_analysis_item(db, item_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Hazard analysis item not found")
    if (item.approval_status or "").lower() == "approved":
        raise HTTPException(status_code=403, detail="Approved items are immutable; create a new version instead.")
    item = ha_item_crud.update_hazard_analysis_item(db, item_id, payload)
    return {"id": item.id, "approval_status": item.approval_status}


@router.post("/hazard-analysis/items/{item_id}/approve", status_code=status.HTTP_200_OK)
def approve_hazard_analysis_item(
    project_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    item = ha_item_crud.approve_hazard_analysis_item(db, item_id, approved_by=current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Hazard analysis item not found")
    return {"id": item.id, "approval_status": "approved"}


@router.post("/hazard-analysis/items/{item_id}/fill-gaps", response_model=Dict[str, Any])
def fill_gaps_hazard_analysis_item(
    project_id: str,
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Call AI to fill only blank/draft fields; do not overwrite approved or existing content."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    item = ha_item_crud.get_hazard_analysis_item(db, item_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=404, detail="Hazard analysis item not found")
    if (item.approval_status or "").lower() == "approved":
        raise HTTPException(status_code=403, detail="Cannot modify approved item.")
    from services.hazard_analysis_ai_service import generate_hazard_analysis_item_with_ai, merge_ai_into_item
    device_name, intended_use = _project_profile_context(db, project_id)
    existing = {
        "hazard": item.hazard, "failure_mode": item.failure_mode, "harm": item.harm,
        "foreseeable_sequence_of_events": item.foreseeable_sequence_of_events,
        "hazardous_situation": item.hazardous_situation, "approval_status": item.approval_status,
    }
    profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    use_env = getattr(profile, "use_environment", None) if profile else None
    ai_out = generate_hazard_analysis_item_with_ai(
        device_type=device_name,
        component_name=item.component.name if item.component else None,
        intended_use=intended_use,
        use_environment=use_env,
        fmea_row=None,
        hazard_category=item.hazard_category,
    )
    merged = merge_ai_into_item(existing, ai_out, only_blank=True)
    update = HazardAnalysisItemUpdate(
        hazard=merged.get("hazard"),
        failure_mode=merged.get("failure_mode"),
        harm=merged.get("harm"),
        foreseeable_sequence_of_events=merged.get("foreseeable_sequence_of_events"),
        hazardous_situation=merged.get("hazardous_situation"),
        initial_severity=merged.get("initial_severity"),
        initial_probability=merged.get("initial_probability"),
        initial_risk_level=merged.get("initial_risk_level"),
        risk_control_measures=merged.get("risk_control_measures"),
        residual_severity=merged.get("residual_severity"),
        residual_probability=merged.get("residual_probability"),
        residual_risk_level=merged.get("residual_risk_level"),
        residual_risk_acceptability=merged.get("residual_risk_acceptability"),
        ai_generated=True,
        ai_confidence=merged.get("ai_confidence"),
        assumptions=merged.get("assumptions"),
    )
    update_data = update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "ai_confidence": item.ai_confidence}


@router.post("/hazard-analysis/items/sync-from-fmea", response_model=Dict[str, Any])
def sync_hazard_analysis_from_fmea(
    project_id: str,
    component_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update hazard analysis items from FMEA rows (prefill draft content)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    from models.fmea import FMEARow
    from models.component import Component
    q = db.query(FMEARow).filter(FMEARow.project_id == project_id)
    if component_id:
        q = q.filter(FMEARow.component_id == component_id)
    fmea_rows = q.all()
    created = 0
    create_fields = set(HazardAnalysisItemCreate.model_fields.keys())
    for fmea in fmea_rows:
        comp_name = None
        if fmea.component_id:
            c = db.query(Component).filter(Component.id == fmea.component_id).first()
            if c:
                comp_name = c.name
        data = fmea_row_to_hazard_analysis_dict(
            fmea, component_name=comp_name, project_id=project_id, component_id=fmea.component_id
        )
        payload_dict = {"project_id": project_id}
        for k, v in data.items():
            if k in create_fields:
                payload_dict[k] = v
        try:
            payload = HazardAnalysisItemCreate(**payload_dict)
            ha_item_crud.create_hazard_analysis_item(db, payload, created_by=current_user.id)
            created += 1
        except Exception:
            pass
    return {"project_id": project_id, "created": created, "fmea_rows_processed": len(fmea_rows)}


@router.get("/hazard-analysis/data", response_model=List[Dict[str, Any]])
def get_hazard_analysis_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    version_scope: str = Query("approved_only", description="Version scope: approved_only, current, all"),
    include_unapproved: bool = Query(False, description="Include unapproved versions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Hazard Analysis data as JSON (for UI table preview)"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse component filter
    component_filter = None
    if components:
        component_names = [name.strip() for name in components.split(",")]
        component_filter = [{"name": name} for name in component_names]
    
    # Build evidence
    evidence = hazard_analysis_builder.build_hazard_analysis(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=version_scope,
        include_unapproved=include_unapproved
    )
    
    # Return rows as JSON
    return evidence.get("rows", [])

