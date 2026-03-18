from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import document as doc_schemas
from crud import document as doc_crud
from crud import project as project_crud
from typing import List, Optional
from fastapi.responses import HTMLResponse, Response
from datetime import datetime, timezone
import io
import json
import csv

router = APIRouter(prefix="/projects/{project_id}", tags=["Document Control"], dependencies=[Depends(require_pro)])

SYSTEM_COMPILED_START = "\n--- SYSTEM COMPILED SECTION START ---\n"
SYSTEM_COMPILED_END = "\n--- SYSTEM COMPILED SECTION END ---\n"


def _upsert_system_compiled_section(existing: str, compiled: str) -> str:
    """
    Insert/replace a system-generated compiled section without overwriting user-authored content.
    Used for compile-only documents (regulatory/audit outputs).
    """
    base = existing or ""
    if SYSTEM_COMPILED_START in base and SYSTEM_COMPILED_END in base:
        pre = base.split(SYSTEM_COMPILED_START, 1)[0]
        post = base.split(SYSTEM_COMPILED_END, 1)[1]
        return pre.rstrip() + SYSTEM_COMPILED_START + (compiled or "").strip() + SYSTEM_COMPILED_END + post.lstrip()
    if base.strip():
        return base.rstrip() + "\n" + SYSTEM_COMPILED_START + (compiled or "").strip() + SYSTEM_COMPILED_END
    return SYSTEM_COMPILED_START + (compiled or "").strip() + SYSTEM_COMPILED_END


def _render_text_as_html(*, title: str, project_name: str, doc_type: str, status: str, version: int, text: str) -> str:
    safe_content = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>{title} — v{version}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 32px; }}
      h1 {{ margin: 0 0 8px 0; }}
      .meta {{ color: #555; margin-bottom: 16px; }}
      pre {{ background: #f7f7f7; padding: 16px; border-radius: 8px; white-space: pre-wrap; }}
      .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <div class="meta">
      <span class="badge">{doc_type}</span>
      &nbsp; Project: {project_name} &nbsp;|&nbsp; Status: {status} &nbsp;|&nbsp; Version: {version}
    </div>
    <pre>{safe_content}</pre>
  </body>
</html>"""

def _safe_meta(d: any) -> dict:
    return d if isinstance(d, dict) else {}


def _append_ai_sample_section(existing: str, draft: str) -> str:
    divider = "\n" + ("=" * 72) + "\n"
    header = (
        f"{divider}"
        "AI Sample / Draft\n"
        "AI samples are examples only and must be reviewed before use.\n"
        f"{divider}\n"
    )
    base = (existing or "").rstrip()
    if base:
        return base + "\n\n" + header + (draft or "").strip() + "\n"
    return header + (draft or "").strip() + "\n"

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

    # RMF is compiled and must not be manually edited.
    existing = doc_crud.get_document(db, document_id, project_id)
    if existing and (existing.type or "").lower() == "rmf":
        update_data = document.model_dump(exclude_unset=True) if hasattr(document, "model_dump") else document.dict(exclude_unset=True)
        if "content" in update_data:
            raise HTTPException(
                status_code=403,
                detail="RMF is a compiled document and cannot be edited manually. Use 'Compile Risk Management File'.",
            )
    
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
    stored_content: Optional[str] = None

    if doc_type == "rmf":
        # Evidence-based compilation: RMF is compiled from authoritative project documents.
        # It must not invent content; it only references document existence/status and links.
        from services.rmf_compiler import compile_rmf
        rendered_html, _ready = compile_rmf(db, project_id=project_id, project_name=project.name)
    elif doc_type == "hazard_analysis":
        from business_logic import hazard_analysis_builder, hazard_analysis_renderer
        from models.project_profile import ProjectProfile
        evidence = hazard_analysis_builder.build_hazard_analysis(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            version_scope=version_scope,
            include_unapproved=bool(options.get("include_unapproved", False)),
        )
        profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
        device_name = getattr(profile, "device_description", None) if profile else None
        intended_use = getattr(profile, "intended_use", None) if profile else None
        rendered_html = hazard_analysis_renderer.render_hazard_analysis_html(
            evidence, project.name, device_name=device_name, intended_use=intended_use
        )
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
        from models.component import Component as ComponentModel

        components = db.query(ComponentModel).filter(ComponentModel.project_id == project_id).all()
        component_name_by_id = {str(c.id): str(c.name or "") for c in components}

        rows = (
            db.query(FMEARow)
            .filter(FMEARow.project_id == project_id)
            .order_by(FMEARow.created_at.asc(), FMEARow.id.asc())
            .all()
        )
        trs = []
        for idx, r in enumerate(rows):
            display_id = f"FMEA-{str(idx + 1).zfill(2)}"
            hazard = ""
            try:
                if isinstance(getattr(r, "ai_metadata", None), dict):
                    hazard = str(r.ai_metadata.get("hazard") or "")
            except Exception:
                hazard = ""
            component_name = ""
            try:
                # Prefer the normalized component name from the project component list.
                if getattr(r, "component_id", None):
                    component_name = component_name_by_id.get(str(r.component_id), "") or ""
                # Fallback: some rows (e.g., AI-generated samples) may not have component_id set.
                if not component_name and isinstance(getattr(r, "ai_metadata", None), dict):
                    meta = r.ai_metadata
                    component_name = str(
                        meta.get("component_name")
                        or meta.get("component")
                        or meta.get("Component")
                        or meta.get("componentName")
                        or ""
                    ).strip()
            except Exception:
                component_name = ""
            # Color-code RPN as low / medium / high for quick scanning.
            rpn_val = None
            try:
                rpn_val = int(r.rpn) if r.rpn is not None else None
            except Exception:
                rpn_val = None
            if rpn_val is None:
                rpn_html = ""
            else:
                rpn_class = "rpn-low"
                if rpn_val >= 100:
                    rpn_class = "rpn-high"
                elif rpn_val >= 50:
                    rpn_class = "rpn-med"
                rpn_html = f"<span class='rpn-pill {rpn_class}'>{rpn_val}</span>"

            trs.append(
                f"<tr><td>{display_id}</td><td>{component_name}</td><td>{hazard}</td><td>{r.failure_mode or ''}</td><td>{r.effect or ''}</td><td>{r.cause or ''}</td>"
                f"<td>{r.severity or ''}</td><td>{r.probability or ''}</td><td>{r.detection or ''}</td>"
                f"<td style='text-align:center'>{rpn_html}</td><td>{r.mitigation or ''}</td></tr>"
            )
        empty_banner = ""
        if not trs:
            # Make the "empty export" case obvious in the UI (otherwise it looks like nothing happened).
            empty_banner = (
                "<div style='margin:12px 0;padding:12px;border:1px solid #fbbf24;background:#fffbeb;color:#92400e;border-radius:8px'>"
                "<b>No saved FMEA rows found for this project.</b> "
                "Generate FMEA rows in the FMEA Generator and click <b>Save to Project</b>, then regenerate this document."
                "</div>"
            )
        rendered_html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>FMEA — {project.name}</title>
<style>
  body{{font-family:Arial,sans-serif;margin:24px}}
  table{{border-collapse:collapse;width:100%}}
  th,td{{border:1px solid #ddd;padding:8px;vertical-align:top}}
  th{{background:#f3f4f6}}
  .rpn-pill{{display:inline-block;padding:2px 10px;border-radius:9999px;font-weight:700;font-size:12px}}
  .rpn-low{{background:#dcfce7;color:#166534}}
  .rpn-med{{background:#fef9c3;color:#854d0e}}
  .rpn-high{{background:#fee2e2;color:#991b1b}}
</style>
</head><body>
<h1>FMEA</h1>
<div>Project: {project.name}</div>
<div>Generated: {datetime.now(timezone.utc).isoformat()}</div>
{empty_banner}
<table><thead><tr><th>ID</th><th>Component</th><th>Hazard</th><th>Failure Mode</th><th>Effect</th><th>Cause</th><th>S</th><th>O</th><th>D</th><th>RPN</th><th>Mitigation</th></tr></thead>
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
    elif doc_type == "design_inputs_doc":
        from business_logic import design_inputs_report_builder, design_inputs_report_renderer
        evidence = design_inputs_report_builder.build_design_inputs_report_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            status_filter=options.get("status"),
            search=options.get("search"),
            missing_output=options.get("missing_output"),
            missing_verification=options.get("missing_verification"),
            # Default: include unlinked requirements so wizard-seeded Design Inputs are visible immediately.
            include_unlinked=bool(options.get("include_unlinked", True)),
        )
        rendered_html = design_inputs_report_renderer.render_design_inputs_html(evidence, project.name)
    elif doc_type == "vv_evidence":
        from business_logic import vv_evidence_report_builder, vv_evidence_report_renderer
        evidence = vv_evidence_report_builder.build_vv_evidence_report_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
            test_type=options.get("test_type"),
            status=options.get("status"),
            unlinked_only=options.get("unlinked_only"),
            missing_acceptance_criteria=options.get("missing_acceptance_criteria"),
            missing_design_output_link=options.get("missing_design_output_link"),
            search=options.get("search"),
        )
        rendered_html = vv_evidence_report_renderer.render_vv_evidence_html(evidence, project.name)
    elif doc_type == "design_outputs_doc":
        from business_logic import design_outputs_doc_builder, design_outputs_doc_renderer
        evidence = design_outputs_doc_builder.build_design_outputs_doc_evidence(
            db=db,
            project_id=project_id,
            component_filter=component_filter,
        )
        rendered_html = design_outputs_doc_renderer.render_design_outputs_doc_html(evidence)
    elif doc_type == "risk_acceptability_criteria":
        from services.risk_acceptability_criteria_service import build_report
        from business_logic.risk_acceptability_criteria_renderer import render_risk_acceptability_criteria_html
        from models.project_profile import ProjectProfile
        from models.risk_acceptability_criteria import RiskAcceptabilityCriteria

        profile = db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
        report = build_report(
            db,
            project_id=project_id,
            project_name=project.name,
            profile=profile,
            generated_by=str(current_user.id) if current_user else None,
            include_ai_narrative=bool(options.get("use_ai", False)),
        )
        rendered_html = render_risk_acceptability_criteria_html(report)
        stored_content = rendered_html  # document content = HTML for viewing; full JSON in RiskAcceptabilityCriteria
        # Persist to RiskAcceptabilityCriteria for versioning and API
        latest = (
            db.query(RiskAcceptabilityCriteria)
            .filter(RiskAcceptabilityCriteria.project_id == project_id)
            .order_by(RiskAcceptabilityCriteria.generated_at.desc())
            .first()
        )
        next_version = (latest.version + 1) if latest else 1
        rac = RiskAcceptabilityCriteria(
            project_id=project_id,
            version=next_version,
            status="draft",
            title=f"Risk Acceptability Criteria — {project.name}",
            content_json=json.dumps(report, default=str),
            content_html=rendered_html,
            source_metadata=report.get("source_metadata"),
            generated_by=str(current_user.id) if current_user else None,
        )
        db.add(rac)
        db.commit()
    elif doc_type in {"essential_requirements_checklist", "submission_index", "audit_package"}:
        # Compile-only documents: links/status only, no compliance claims, do not overwrite user-authored content.
        from services.regulatory_audit_compiler import (
            compile_audit_package,
            compile_essential_requirements_checklist,
            compile_submission_index,
        )

        if doc_type == "essential_requirements_checklist":
            compiled = compile_essential_requirements_checklist(db, project_id=project_id, project_name=project.name)
        elif doc_type == "submission_index":
            compiled = compile_submission_index(db, project_id=project_id, project_name=project.name)
        else:
            compiled = compile_audit_package(db, project_id=project_id, project_name=project.name)

        stored_content = _upsert_system_compiled_section(document.content or "", compiled)
        rendered_html = _render_text_as_html(
            title=document.name,
            project_name=project.name,
            doc_type=doc_type,
            status="draft",
            version=(document.version or 0) + 1,
            text=stored_content,
        )
    else:
        # Minimal deterministic fallback
        rendered_html = f"""<!doctype html>
<html><head><meta charset="utf-8"/><title>{document.name} — {project.name}</title></head>
<body><h1>{document.name}</h1><p>Project: {project.name}</p><pre>{document.content or ''}</pre></body></html>"""
        stored_content = document.content or ""

    # Create new version (do not overwrite silently)
    document.version += 1
    document.content = stored_content if stored_content is not None else rendered_html
    document.status = "draft"  # generation creates a new draft version
    document.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(document)

    doc_crud.create_document_version(
        db,
        document.id,
        document.version,
        document.content,
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


@router.post("/documents/{document_type}/ai-sample", response_model=doc_schemas.DocumentOut)
def generate_ai_sample(
    project_id: str,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an opt-in AI Sample / Draft for a document type.

    Hard rules:
    - Must not overwrite user-entered content (we append in a NEW document version)
    - Must be clearly labeled as AI Sample / Draft
    - Must set ai_metadata flags so UI can hide the button once generated
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    doc_type = (document_type or "").strip().lower()
    if not doc_type:
        raise HTTPException(status_code=400, detail="document_type is required")

    # Some document types (e.g., RMF) must not invent content.
    from services.document_guidance_registry import get_document_guidance_registry

    reg = get_document_guidance_registry()
    entry = reg.get(doc_type)
    if entry and not bool(entry.get("ai_available", False)):
        raise HTTPException(status_code=400, detail=f"AI sample is not available for '{doc_type}'")

    doc = doc_crud.get_document_by_type(db, project_id=project_id, doc_type=doc_type)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document of type '{doc_type}' not found for project")

    meta0 = _safe_meta(getattr(doc, "ai_metadata", None))
    if meta0.get("ai_sample_generated") is True or meta0.get("default_sample_provided") is True:
        raise HTTPException(status_code=409, detail="AI sample already provided for this document")

    # Build a deterministic context pack (ProjectProfile + Components) like other AI services.
    from crud import project_profile as profile_crud
    from crud import component as component_crud
    from services.project_profile_initializer import build_project_setup_scaffolds

    profile = profile_crud.get_project_profile(db, project_id)
    components = component_crud.get_components_by_project(db, project_id)
    scaffolds = build_project_setup_scaffolds(db, project_id=project_id)

    component_lines = [
        f"- {getattr(c, 'name', '')} (id={getattr(c, 'id', '')})" + (f": {getattr(c, 'description', '')}" if getattr(c, "description", None) else "")
        for c in components
    ]
    scaffold = scaffolds.get(doc_type) if isinstance(scaffolds, dict) else None
    context = (
        f"Project ID: {project_id}\n"
        f"Project name: {project.name}\n"
        "Profile:\n"
        f"- intended_use: {getattr(profile, 'intended_use', None)}\n"
        f"- device_description: {getattr(profile, 'device_description', None)}\n"
        f"- user_population: {getattr(profile, 'user_population', None)}\n"
        f"- use_environment: {getattr(profile, 'use_environment', None)}\n"
        f"- key_safety_characteristics: {getattr(profile, 'key_safety_characteristics', None)}\n\n"
        "Components:\n"
        + ("\n".join(component_lines) if component_lines else "- (none)\n")
        + "\n\n"
        + ("Deterministic scaffold (reference only):\n" + (scaffold or "(none)") + "\n")
    )

    # Generate with OpenAI (explicit opt-in; endpoint is only called on user click).
    try:
        from services.project_ai_doc_generator import _default_ai_draft_fn

        draft = _default_ai_draft_fn(
            doc_type,
            context,
            {
                "project_id": project_id,
                "project_name": project.name,
                "doc_type": doc_type,
                "mode": "ai_sample",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

    now = datetime.now(timezone.utc).isoformat()
    new_meta = {
        **meta0,
        "ai_sample_generated": True,
        "ai_sample_generated_at": now,
        "ai_sample_source": "document_ai_sample_endpoint",
        "generated_with_ai": True,
    }

    new_content = _append_ai_sample_section(doc.content or "", draft)
    updated = doc_crud.update_document(
        db,
        doc.id,
        doc_schemas.DocumentUpdate(content=new_content, status="draft", ai_metadata=new_meta),
        project_id,
    )
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update document")
    return updated


@router.post("/documents/{document_type}/generate-ai", response_model=doc_schemas.DocumentOut)
def generate_ai_example(
    project_id: str,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an AI-GENERATED EXAMPLE draft for ANY document type.

    Hard rules:
    - Must not overwrite user-entered content (append as a clearly marked AI Example section)
    - Must create a NEW document version
    - Must be labeled Draft + AI Example + generated_at timestamp
    """
    from services.document_ai_example import generate_ai_example_for_document

    return generate_ai_example_for_document(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        document_type=document_type,
    )


@router.post("/documents/{document_type}/generate-with-ai", response_model=doc_schemas.DocumentOut)
def generate_with_ai_populate(
    project_id: str,
    document_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Populate a document draft with applicable AI-generated content.

    Behavior:
    - If the document is empty/scaffold/placeholder-heavy, overwrite it with a new AI draft (new version).
    - Otherwise, append an addendum to preserve user edits (new version).
    """
    from services.document_ai_populate import generate_ai_populated_draft_for_document

    return generate_ai_populated_draft_for_document(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
        document_type=document_type,
    )


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

    # For deterministic exports, render from authoritative DB evidence by default (current view).
    # If a specific version is requested, export that version's stored content for auditability.
    doc_type = (document.type or "").lower()
    if version is None and doc_type == "traceability_matrix":
        from business_logic import traceability_matrix_builder, traceability_matrix_renderer

        evidence = traceability_matrix_builder.build_traceability_matrix_evidence(
            db=db,
            project_id=project_id,
            component_filter=None,
        )
        html = traceability_matrix_renderer.render_traceability_matrix_html(evidence, project.name)
        return HTMLResponse(content=html)

    if version is None and doc_type == "design_inputs_doc":
        # Deterministic export: always compile from current DB state by default.
        from business_logic import design_inputs_report_builder, design_inputs_report_renderer

        evidence = design_inputs_report_builder.build_design_inputs_report_evidence(
            db=db,
            project_id=project_id,
            component_filter=None,
            status_filter=None,
            search=None,
            missing_output=None,
            missing_verification=None,
            include_unlinked=True,
        )
        html = design_inputs_report_renderer.render_design_inputs_html(evidence, project.name)
        return HTMLResponse(content=html)

    if version is None and doc_type == "design_outputs_doc":
        # Deterministic export: always compile from current DB state by default.
        from business_logic import design_outputs_doc_builder, design_outputs_doc_renderer

        evidence = design_outputs_doc_builder.build_design_outputs_doc_evidence(
            db=db,
            project_id=project_id,
            component_filter=None,
        )
        html = design_outputs_doc_renderer.render_design_outputs_doc_html(evidence)
        return HTMLResponse(content=html)

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


@router.get("/documents/{document_id}/export/csv")
def export_document_csv(
    project_id: str,
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export a document as CSV.

    Currently supported:
    - FMEA: exports a deterministic table from persisted FMEA rows
    """
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    document = doc_crud.get_document(db, document_id, project_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_type = (document.type or "").lower()
    if doc_type != "fmea":
        raise HTTPException(status_code=400, detail="CSV export is only supported for FMEA documents")

    from models.fmea import FMEARow
    from models.component import Component as ComponentModel

    components = db.query(ComponentModel).filter(ComponentModel.project_id == project_id).all()
    component_name_by_id = {str(c.id): str(c.name or "") for c in components}

    rows = (
        db.query(FMEARow)
        .filter(FMEARow.project_id == project_id)
        .order_by(FMEARow.created_at.asc(), FMEARow.id.asc())
        .all()
    )

    def _component_name_for_row(r: FMEARow) -> str:
        # Prefer component_id lookup, fallback to ai_metadata fields.
        try:
            if getattr(r, "component_id", None):
                name = component_name_by_id.get(str(r.component_id), "") or ""
                if name:
                    return name
        except Exception:
            pass
        try:
            md = getattr(r, "ai_metadata", None)
            if isinstance(md, dict):
                return str(
                    md.get("component_name")
                    or md.get("component")
                    or md.get("Component")
                    or md.get("componentName")
                    or ""
                ).strip()
        except Exception:
            pass
        return ""

    def _hazard_for_row(r: FMEARow) -> str:
        try:
            md = getattr(r, "ai_metadata", None)
            if isinstance(md, dict):
                return str(md.get("hazard") or "")
        except Exception:
            return ""
        return ""

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["ID", "Component", "Hazard", "Failure Mode", "Effect", "Cause", "S", "O", "D", "RPN", "Mitigation"])
    for idx, r in enumerate(rows):
        display_id = f"FMEA-{str(idx + 1).zfill(2)}"
        w.writerow(
            [
                display_id,
                _component_name_for_row(r),
                _hazard_for_row(r),
                getattr(r, "failure_mode", None) or "",
                getattr(r, "effect", None) or "",
                getattr(r, "cause", None) or "",
                getattr(r, "severity", None) or "",
                getattr(r, "probability", None) or "",
                getattr(r, "detection", None) or "",
                getattr(r, "rpn", None) or "",
                getattr(r, "mitigation", None) or "",
            ]
        )

    filename = f"FMEA_{project.name}_v{document.version}.csv".replace(" ", "_")
    return Response(
        content=out.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

