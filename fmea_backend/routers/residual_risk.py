from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from business_logic import residual_risk_builder, residual_risk_renderer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects/{project_id}", tags=["Residual Risk Evaluation"])

class ComponentFilter(BaseModel):
    id: Optional[str] = None
    name: str

class ResidualRiskGenerateRequest(BaseModel):
    components: Optional[List[ComponentFilter]] = None
    version_scope: str = "approved_only"  # approved_only, current, all
    include_unapproved: bool = False
    acceptability_profile: str = "default_med_device"
    custom_thresholds: Optional[Dict[str, Any]] = None
    format: str = "html"

@router.post("/residual-risk/generate", status_code=status.HTTP_200_OK)
def generate_residual_risk(
    project_id: str,
    request: ResidualRiskGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Residual Risk Evaluation HTML report"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Build evidence
    component_filter = None
    if request.components:
        component_filter = [{"id": c.id, "name": c.name} for c in request.components]
    
    evidence = residual_risk_builder.build_residual_risk_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=request.version_scope,
        include_unapproved=request.include_unapproved,
        custom_thresholds=request.custom_thresholds,
        acceptability_profile=request.acceptability_profile
    )
    
    # Render HTML
    residual_risk_html = residual_risk_renderer.render_residual_risk_html(evidence, project.name)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "version_scope": request.version_scope,
        "residual_risk_html": residual_risk_html,
        "counts": evidence.get("counts", {})
    }

@router.get("/residual-risk/export", response_class=HTMLResponse)
def export_residual_risk(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    version_scope: str = Query("approved_only", description="Version scope: approved_only, current, all"),
    include_unapproved: bool = Query(False, description="Include unapproved versions"),
    format: str = Query("html", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export Residual Risk Evaluation as HTML file"""
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
    evidence = residual_risk_builder.build_residual_risk_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=version_scope,
        include_unapproved=include_unapproved
    )
    
    # Render HTML
    residual_risk_html = residual_risk_renderer.render_residual_risk_html(evidence, project.name)
    
    return HTMLResponse(content=residual_risk_html)

@router.get("/residual-risk/data", response_model=List[Dict[str, Any]])
def get_residual_risk_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    version_scope: str = Query("approved_only", description="Version scope: approved_only, current, all"),
    include_unapproved: bool = Query(False, description="Include unapproved versions"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Residual Risk Evaluation data as JSON (for UI table preview)"""
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
    evidence = residual_risk_builder.build_residual_risk_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=version_scope,
        include_unapproved=include_unapproved
    )
    
    # Return rows as JSON
    return evidence.get("rows", [])

