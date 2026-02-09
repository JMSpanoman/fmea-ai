from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from business_logic import hazard_analysis_builder, hazard_analysis_renderer
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects/{project_id}", tags=["Hazard Analysis"])

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
        include_unapproved=request.include_unapproved
    )
    
    # Render HTML
    hazard_analysis_html = hazard_analysis_renderer.render_hazard_analysis_html(evidence, project.name)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "version_scope": request.version_scope,
        "hazard_analysis_html": hazard_analysis_html,
        "counts": evidence.get("counts", {})
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
    
    # Build evidence
    evidence = hazard_analysis_builder.build_hazard_analysis(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        version_scope=version_scope,
        include_unapproved=include_unapproved
    )
    
    # Render HTML
    hazard_analysis_html = hazard_analysis_renderer.render_hazard_analysis_html(evidence, project.name)
    
    return HTMLResponse(content=hazard_analysis_html)

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

