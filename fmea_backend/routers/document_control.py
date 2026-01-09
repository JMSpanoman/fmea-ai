from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import document as doc_schemas
from crud import document as doc_crud
from crud import project as project_crud
from typing import List, Optional
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/projects/{project_id}", tags=["Document Control"])

@router.get("/documents", response_model=List[doc_schemas.DocumentOut])
def get_documents(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all documents for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return doc_crud.get_documents_by_project(db, project_id)

@router.post("/documents", response_model=doc_schemas.DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    project_id: str,
    document: doc_schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter
    if hasattr(document, 'model_copy'):
        document = document.model_copy(update={'project_id': project_id})
    else:
        document_dict = document.dict() if hasattr(document, 'dict') else document.model_dump()
        document_dict['project_id'] = project_id
        document = doc_schemas.DocumentCreate(**document_dict)
    
    return doc_crud.create_document(db, document)

@router.get("/documents/{document_id}", response_model=doc_schemas.DocumentOut)
def get_document(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.put("/documents/{document_id}", response_model=doc_schemas.DocumentOut)
def update_document(
    project_id: str,
    document_id: str,
    document: doc_schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_doc = doc_crud.update_document(db, document_id, document, project_id)
    if not updated_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return updated_doc

@router.post("/documents/{document_id}/approve", response_model=doc_schemas.DocumentOut)
def approve_document(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a document with automatic training assignment"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Use business logic for approval workflow
    from business_logic.approval_workflow import approve_document_with_workflow
    
    result = approve_document_with_workflow(db, document_id, project_id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Auto-assign training to project team
    from business_logic.training_auto_assignment import auto_assign_training_on_document_approval
    auto_assign_training_on_document_approval(db, document_id, project_id)
    
    return result["document"]

@router.get("/documents/{document_id}/versions", response_model=List[doc_schemas.DocumentVersionOut])
def get_document_versions(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions of a document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    versions = doc_crud.get_document_versions(db, document_id)
    return versions


@router.get("/documents/{document_id}/versions/{version_no}", response_model=doc_schemas.DocumentVersionOut)
def get_document_version(
    project_id: str,
    document_id: str,
    version_no: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific version of a document"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    v = doc_crud.get_document_version_by_no(db, document_id, version_no)
    if not v:
        raise HTTPException(status_code=404, detail="Document version not found")
    return v


@router.post("/documents/{document_id}/generate", response_model=doc_schemas.DocumentGenerateResponse)
def generate_document_version(
    project_id: str,
    document_id: str,
    request: doc_schemas.DocumentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new document version (audit-friendly)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    component_filter = None
    if request.components:
        component_filter = [{"id": c.id, "name": c.name} for c in request.components]

    version_scope = request.version_scope or "approved_only"
    options = request.options or {}

    # Build deterministic HTML by doc.type using existing evidence builders/renderers
    doc_type = (document.type or "").lower()
    rendered_html: str

    if doc_type == "rmf":
        from business_logic import rmf_builder, rmf_renderer
        evidence = rmf_builder.build_rmf_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            include_ai_events=bool(options.get("include_ai_events", False)),
            include_audit_log=bool(options.get("include_audit_log", False)),
            include_traceability=bool(options.get("include_traceability", True)),
        )
        rendered_html = rmf_renderer.render_rmf_html(evidence, project.name)
    elif doc_type == "hazard_analysis":
        from business_logic import hazard_analysis_builder, hazard_analysis_renderer
        evidence = hazard_analysis_builder.build_hazard_analysis(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            version_scope=version_scope,
            include_unapproved=bool(options.get("include_unapproved", False)),
        )
        rendered_html = hazard_analysis_renderer.render_hazard_analysis_html(evidence, project.name)
    elif doc_type == "residual_risk":
        from business_logic import residual_risk_builder, residual_risk_renderer
        evidence = residual_risk_builder.build_residual_risk_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            version_scope=version_scope,
            include_unapproved=bool(options.get("include_unapproved", False)),
            acceptability_profile=str(options.get("acceptability_profile", "default_med_device")),
            custom_thresholds=options.get("custom_thresholds"),
        )
        rendered_html = residual_risk_renderer.render_residual_risk_html(evidence, project.name)
    elif doc_type == "risk_controls_doc":
        from business_logic import risk_controls_doc_builder, risk_controls_doc_renderer
        evidence = risk_controls_doc_builder.build_risk_controls_doc_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            include_only_active_controls=bool(options.get("active_controls_only", True)),
            version_scope=str(options.get("version_scope", "current")),
            include_traceability_details=bool(options.get("include_traceability", True)),
        )
        rendered_html = risk_controls_doc_renderer.render_risk_controls_doc_html(evidence, project.name)
    elif doc_type == "fmea":
        # Deterministic table export from persisted FMEA rows
        from models.fmea import FMEARow
        rows = db.query(FMEARow).filter(FMEARow.project_id == project_id).all()
        trs = []
        for r in rows:
            trs.append(
                f"<tr><td>{r.id}</td><td>{r.failure_mode or ''}</td><td>{r.effect or ''}</td><td>{r.cause or ''}</td>"
                f"<td>{r.severity or ''}</td><td>{r.probability or ''}</td><td>{r.detection or ''}</td>"
                f"<td>{r.rpn or ''}</td><td>{r.mitigation or ''}</td></tr>"
            )
        rendered_html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>FMEA — {project.name}</title>
<style>body{{font-family:Arial,sans-serif;margin:24px}} table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #ddd;padding:8px}} th{{background:#f3f4f6}}</style>
</head><body>
<h1>FMEA</h1>
<div>Project: {project.name}</div>
<div>Generated: {datetime.now(timezone.utc).isoformat()}</div>
<table><thead><tr><th>ID</th><th>Failure Mode</th><th>Effect</th><th>Cause</th><th>S</th><th>P</th><th>D</th><th>RPN</th><th>Mitigation</th></tr></thead>
<tbody>{''.join(trs) if trs else ''}</tbody></table>
</body></html>"""
    elif doc_type == "rmp":
        # Deterministic Risk Management Plan generation (ISO 14971) using defaults + selected components.
        from business_logic import rmp_generator
        from models.component import Component as ComponentModel

        # Inputs (with safe defaults)
        scope = str(options.get("scope") or "TBD (edit Scope in Generate New modal)")
        intended_use = str(options.get("intended_use") or "TBD (edit Intended Use in Generate New modal)")
        acceptability_profile = str(options.get("acceptability_profile") or "default_med_device")

        review_roles = options.get("review_roles") or {
            "risk_manager": "required",
            "design_lead": "required",
            "quality_lead": "required",
            "approver": "required",
        }
        if not isinstance(review_roles, dict):
            review_roles = {"risk_manager": "required"}

        # Components: if none provided, use all project components (or a single placeholder)
        comps_in: list[dict[str, str]] = []
        if component_filter:
            for c in component_filter:
                name = (c.get("name") or c.get("id") or "").strip()
                if name:
                    comps_in.append({"name": name, "description": ""})
        else:
            comps = db.query(ComponentModel).filter(ComponentModel.project_id == project_id).all()
            for c in comps:
                comps_in.append({"name": c.name, "description": c.description or ""})

        if not comps_in:
            comps_in = [{"name": "All components", "description": ""}]

        acceptability_criteria = rmp_generator.generate_acceptability_criteria(acceptability_profile)
        rendered_html = rmp_generator.generate_rmp_html(
            title=f"Risk Management Plan (RMP) — {project.name}",
            scope=scope,
            intended_use=intended_use,
            components=[rmp_generator.ComponentInput(**c) for c in comps_in],
            acceptability_criteria=acceptability_criteria,
            risk_methodology=rmp_generator.generate_risk_methodology(),
            review_roles=review_roles,
            risk_control_categories=rmp_generator.generate_risk_control_categories(),
            benefit_risk_criteria=rmp_generator.generate_benefit_risk_criteria(),
            lifecycle_linkage=rmp_generator.generate_lifecycle_linkage(),
            governance_rules=rmp_generator.generate_governance_rules(),
            version_no=document.version + 1,
        )
    elif doc_type == "traceability_matrix":
        from business_logic import traceability_matrix_builder, traceability_matrix_renderer
        evidence = traceability_matrix_builder.build_traceability_matrix_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
        )
        rendered_html = traceability_matrix_renderer.render_traceability_matrix_html(evidence, project.name)
    else:
        # Minimal deterministic fallback
        rendered_html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>{document.name} — {project.name}</title></head>
<body><h1>{document.name}</h1><p>Project: {project.name}</p><pre>{document.content or ''}</pre></body></html>"""

    # Create new version (do not overwrite silently)
    document.version += 1
    document.content = rendered_html
    document.status = "draft"  # generation creates a new draft version
    document.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(document)

    doc_crud.create_document_version(
        db,
        document.id,
        document.version,
        rendered_html,
        {
            "generated": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version_scope": version_scope,
            "components": component_filter or [],
            "options": options,
        },
    )

    return {
        "doc_id": document.id,
        "new_version_no": document.version,
        "rendered_html": rendered_html,
        "updated_at": document.updated_at,
    }


@router.get("/documents/{document_id}/export/html", response_class=HTMLResponse)
def export_document_html(
    project_id: str,
    document_id: str,
    version: Optional[int] = Query(None, description="Export a specific version number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export a document as deterministic HTML (MVP)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    content = document.content or ""
    export_version = version or document.version

    if version is not None:
        v = doc_crud.get_document_version_by_no(db, document_id, export_version)
        if not v:
            raise HTTPException(status_code=404, detail="Document version not found")
        content = v.content or ""

    # If content already looks like full HTML, return as-is
    lowered = content.lstrip().lower()
    if lowered.startswith("<!doctype") or lowered.startswith("<html") or lowered.startswith("<!doctype html"):
        return HTMLResponse(content=content)

    # Otherwise wrap as readable HTML with escaped content
    safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{document.name} — v{export_version}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 32px; }}
      h1 {{ margin: 0 0 8px 0; }}
      .meta {{ color: #555; margin-bottom: 16px; }}
      pre {{ background: #f7f7f7; padding: 16px; border-radius: 8px; white-space: pre-wrap; }}
      .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    </style>
  </head>
  <body>
    <h1>{document.name}</h1>
    <div class="meta">
      <span class="badge">{document.type}</span>
      &nbsp; Project: {project.name} &nbsp;|&nbsp; Status: {document.status} &nbsp;|&nbsp; Version: {export_version}
    </div>
    <pre>{safe_content}</pre>
  </body>
</html>"""
    return HTMLResponse(content=html)

