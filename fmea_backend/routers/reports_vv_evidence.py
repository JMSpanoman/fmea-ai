from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.user import User
from crud import project as project_crud
from business_logic import vv_evidence_report_builder, vv_evidence_report_renderer


router = APIRouter(prefix="/projects/{project_id}/reports", tags=["Reports - V&V Evidence"])


def _parse_components_param(components: Optional[str]) -> List[dict]:
    if not components:
        return []
    parts = [p.strip() for p in components.split(",") if p.strip()]
    out = []
    for p in parts:
        if len(p) >= 32 and p.count("-") >= 4:
            out.append({"id": p})
        else:
            out.append({"name": p})
    return out


@router.get("/vv-evidence/data")
def vv_evidence_report_data(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names or ids"),
    test_type: Optional[str] = Query(None, description="verification|validation"),
    status: Optional[str] = Query(None, description="planned|executed|passed|failed|obsolete (or legacy)"),
    unlinked_only: Optional[bool] = Query(None, description="Only rows with no upstream links"),
    missing_acceptance_criteria: Optional[bool] = Query(None, description="Only rows missing acceptance criteria"),
    missing_design_output_link: Optional[bool] = Query(None, description="Only rows missing trace link DO→VV"),
    search: Optional[str] = Query(None, description="Search key/title/method/acceptance"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    component_filter = _parse_components_param(components)
    evidence = vv_evidence_report_builder.build_vv_evidence_report_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        test_type=test_type,
        status=status,
        unlinked_only=unlinked_only,
        missing_acceptance_criteria=missing_acceptance_criteria,
        missing_design_output_link=missing_design_output_link,
        search=search,
    )
    evidence["generated_at"] = None
    return evidence


@router.get("/vv-evidence/export", response_class=HTMLResponse)
def vv_evidence_report_export(
    project_id: str,
    components: Optional[str] = Query(None),
    test_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    unlinked_only: Optional[bool] = Query(None),
    missing_acceptance_criteria: Optional[bool] = Query(None),
    missing_design_output_link: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    format: str = Query("html", description="html only (pdf later)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if format != "html":
        raise HTTPException(status_code=400, detail="Only format=html is supported right now")

    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    component_filter = _parse_components_param(components)
    evidence = vv_evidence_report_builder.build_vv_evidence_report_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        test_type=test_type,
        status=status,
        unlinked_only=unlinked_only,
        missing_acceptance_criteria=missing_acceptance_criteria,
        missing_design_output_link=missing_design_output_link,
        search=search,
    )
    html = vv_evidence_report_renderer.render_vv_evidence_html(evidence, project.name)
    return HTMLResponse(content=html)

