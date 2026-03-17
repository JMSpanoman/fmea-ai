from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.plan import require_pro
from database import get_db
from models.user import User
from crud import project as project_crud
from business_logic import design_inputs_report_builder, design_inputs_report_renderer


router = APIRouter(prefix="/projects/{project_id}/reports", tags=["Reports - Design Inputs"], dependencies=[Depends(require_pro)])


def _parse_components_param(components: Optional[str]) -> List[dict]:
    """
    Parse comma-separated component names or ids into the canonical filter format.
    """
    if not components:
        return []
    parts = [p.strip() for p in components.split(",") if p.strip()]
    out = []
    for p in parts:
        # Heuristic: UUID-like => treat as id, otherwise name.
        if len(p) >= 32 and p.count("-") >= 4:
            out.append({"id": p})
        else:
            out.append({"name": p})
    return out


@router.get("/design-inputs/data")
def design_inputs_report_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    status: Optional[str] = Query(None, description="draft|approved|implemented|obsolete"),
    include_unlinked: bool = Query(False, description="Include design inputs with no upstream risk_control link"),
    missing_output: Optional[bool] = Query(None, description="If true, only show rows missing design output"),
    missing_verification: Optional[bool] = Query(None, description="If true, only show rows missing V&V evidence"),
    search: Optional[str] = Query(None, description="Search DI key/title/requirement text"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    component_filter = _parse_components_param(components)
    evidence = design_inputs_report_builder.build_design_inputs_report_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        status_filter=status,
        search=search,
        missing_output=missing_output,
        missing_verification=missing_verification,
        include_unlinked=include_unlinked,
    )
    evidence["generated_at"] = None  # front-end stamps or uses server time if needed
    return evidence


@router.get("/design-inputs/export", response_class=HTMLResponse)
def design_inputs_report_export(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    status: Optional[str] = Query(None, description="draft|approved|implemented|obsolete"),
    format: str = Query("html", description="html only (pdf later)"),
    include_unlinked: bool = Query(False, description="Include design inputs with no upstream risk_control link"),
    missing_output: Optional[bool] = Query(None, description="If true, only show rows missing design output"),
    missing_verification: Optional[bool] = Query(None, description="If true, only show rows missing V&V evidence"),
    search: Optional[str] = Query(None, description="Search DI key/title/requirement text"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if format != "html":
        raise HTTPException(status_code=400, detail="Only format=html is supported right now")

    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    component_filter = _parse_components_param(components)
    evidence = design_inputs_report_builder.build_design_inputs_report_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        status_filter=status,
        search=search,
        missing_output=missing_output,
        missing_verification=missing_verification,
        include_unlinked=include_unlinked,
    )
    html = design_inputs_report_renderer.render_design_inputs_html(evidence, project.name)
    return HTMLResponse(content=html)

