from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from business_logic import rmf_builder, rmf_renderer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects/{project_id}", tags=["Risk Management File"])

class ComponentFilter(BaseModel):
    id: Optional[str] = None
    name: str

class RMFGenerateRequest(BaseModel):
    components: Optional[List[ComponentFilter]] = None
    include_ai_events: bool = True
    include_audit_log: bool = True
    include_traceability: bool = True
    format: str = "html"

@router.post("/rmf/generate", status_code=status.HTTP_200_OK)
def generate_rmf(
    project_id: str,
    request: RMFGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate RMF HTML evidence report"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Build evidence
    component_filter = None
    if request.components:
        component_filter = [{"id": c.id, "name": c.name} for c in request.components]
    
    evidence = rmf_builder.build_rmf_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_ai_events=request.include_ai_events,
        include_audit_log=request.include_audit_log,
        include_traceability=request.include_traceability
    )
    
    # Render HTML
    rmf_html = rmf_renderer.render_rmf_html(evidence, project.name)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "rmf_html": rmf_html
    }

@router.get("/rmf/export", response_class=HTMLResponse)
def export_rmf(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    format: str = Query("html", description="Export format"),
    include_ai_events: bool = Query(True, description="Include AI events"),
    include_audit_log: bool = Query(True, description="Include audit log"),
    include_traceability: bool = Query(True, description="Include traceability"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export RMF as HTML file"""
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
    evidence = rmf_builder.build_rmf_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_ai_events=include_ai_events,
        include_audit_log=include_audit_log,
        include_traceability=include_traceability
    )
    
    # Render HTML
    rmf_html = rmf_renderer.render_rmf_html(evidence, project.name)
    
    return HTMLResponse(content=rmf_html)

@router.get("/rmf/evidence", response_model=Dict[str, Any])
def get_rmf_evidence(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    include_ai_events: bool = Query(True, description="Include AI events"),
    include_audit_log: bool = Query(True, description="Include audit log"),
    include_traceability: bool = Query(True, description="Include traceability"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get RMF evidence as JSON (for UI preview and future ZIP packaging)"""
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
    evidence = rmf_builder.build_rmf_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        include_ai_events=include_ai_events,
        include_audit_log=include_audit_log,
        include_traceability=include_traceability
    )
    
    # Add summaries
    risk_count = len(evidence.get("risks", []))
    total_versions = sum(len(r.get("versions", [])) for r in evidence.get("risks", []))
    total_controls = sum(len(r.get("controls", [])) for r in evidence.get("risks", []))
    total_approvals = sum(len(r.get("approvals", [])) for r in evidence.get("risks", []))
    
    evidence["summaries"] = {
        "risk_count": risk_count,
        "total_versions": total_versions,
        "total_controls": total_controls,
        "total_approvals": total_approvals,
        "generated_at": datetime.now().isoformat()
    }
    
    return evidence

