from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from business_logic import risk_controls_doc_builder, risk_controls_doc_renderer
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/projects/{project_id}/reports", tags=["Reports - Risk Control Measures"])

@router.get("/risk-control-measures/data")
def get_risk_control_measures_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names or IDs"),
    active_only: bool = Query(True, description="Include only active controls"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Risk Control Measures data as JSON (for UI preview)"""
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
    
    # Format response to match spec
    rows = []
    for row in evidence.get("rows", []):
        formatted_row = {
            "risk_item_id": row.get("risk_item_id"),
            "risk_key": row.get("risk_key"),
            "control_id": row.get("control_id"),
            "control_key": row.get("control_key"),
            "control_name": row.get("control_name"),
            "control_type": row.get("control_type"),
            "control_description": row.get("control_description"),
            "control_status": row.get("control_status"),
            "implementation_refs": [
                {
                    "artifact_type": ref.get("type"),
                    "artifact_id": ref.get("id"),
                    "display": ref.get("display"),
                    "link_type": ref.get("link_type")
                }
                for ref in row.get("implementation_refs", [])
            ],
            "verification_methods": [
                {
                    "artifact_type": method.get("type"),
                    "artifact_id": method.get("id"),
                    "display": method.get("display"),
                    "link_type": method.get("link_type")
                }
                for method in row.get("verification_methods", [])
            ],
            "flags": row.get("flags", {})
        }
        rows.append(formatted_row)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "generated_at": datetime.now().isoformat(),
        "rows": rows,
        "counts": evidence.get("counts", {})
    }

@router.get("/risk-control-measures/export", response_class=HTMLResponse)
def export_risk_control_measures(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names or IDs"),
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

