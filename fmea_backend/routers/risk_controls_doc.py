from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from business_logic import risk_controls_doc_builder, risk_controls_doc_renderer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects/{project_id}", tags=["Risk Control Measures Documentation"])

class ComponentFilter(BaseModel):
    id: Optional[str] = None
    name: str

class RiskControlsDocGenerateRequest(BaseModel):
    components: Optional[List[ComponentFilter]] = None
    include_only_active_controls: bool = True
    version_scope: str = "current"
    include_traceability_details: bool = True
    format: str = "html"

@router.post("/risk-controls-doc/generate", status_code=status.HTTP_200_OK)
def generate_risk_controls_doc(
    project_id: str,
    request: RiskControlsDocGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Risk Control Measures Documentation HTML report"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Build evidence
    component_filter = None
    if request.components:
        component_filter = [{"id": c.id, "name": c.name} for c in request.components]
    
    evidence = risk_controls_doc_builder.build_risk_controls_doc_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_only_active_controls=request.include_only_active_controls,
        version_scope=request.version_scope,
        include_traceability_details=request.include_traceability_details
    )
    
    # Render HTML
    risk_controls_doc_html = risk_controls_doc_renderer.render_risk_controls_doc_html(evidence, project.name)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "risk_controls_doc_html": risk_controls_doc_html,
        "counts": evidence.get("counts", {})
    }

@router.get("/risk-controls-doc/export", response_class=HTMLResponse)
def export_risk_controls_doc(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    active_only: bool = Query(True, description="Include only active controls"),
    format: str = Query("html", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export Risk Control Measures Documentation as HTML file"""
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
    evidence = risk_controls_doc_builder.build_risk_controls_doc_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_only_active_controls=active_only,
        version_scope="current",
        include_traceability_details=True
    )
    
    # Render HTML
    risk_controls_doc_html = risk_controls_doc_renderer.render_risk_controls_doc_html(evidence, project.name)
    
    return HTMLResponse(content=risk_controls_doc_html)

@router.get("/risk-controls-doc/data", response_model=List[Dict[str, Any]])
def get_risk_controls_doc_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    active_only: bool = Query(True, description="Include only active controls"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Risk Control Measures Documentation data as JSON (for UI table preview)"""
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
    evidence = risk_controls_doc_builder.build_risk_controls_doc_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_only_active_controls=active_only,
        version_scope="current",
        include_traceability_details=True
    )
    
    # Return rows as JSON
    return evidence.get("rows", [])

