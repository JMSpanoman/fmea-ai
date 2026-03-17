from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from crud import project as project_crud
from crud import pms_signal as pms_signal_crud
from models.pms_signal import PMSSignal
from crud import traceability as trace_crud
from crud import capa as capa_crud
from crud import change_control_phase3 as cc_crud
from crud import audit_log_event as audit_log_crud
from crud import idempotency as idempotency_crud
from schemas import pms_signal as pms_signal_schemas
from schemas import capa as capa_schemas
from schemas import change_control as cc_schemas
from schemas.trace import TraceLinkCreate
from schemas.audit_log_event import AuditLogEventCreate
from business_logic import pms_signal_report_builder, pms_signal_report_renderer
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/projects/{project_id}/pms", tags=["PMS Signals"], dependencies=[Depends(require_pro)])

# CRUD Endpoints
@router.post("/signals", status_code=status.HTTP_201_CREATED)
def create_pms_signal(
    project_id: str,
    signal: pms_signal_schemas.PMSSignalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new PMS signal"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if signal_key already exists
    existing = db.query(PMSSignal).filter(
        PMSSignal.project_id == project_id,
        PMSSignal.signal_key == signal.signal_key
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Signal key {signal.signal_key} already exists")
    
    return pms_signal_crud.create_pms_signal(db, signal, project_id, current_user.id)

@router.get("/signals", response_model=List[pms_signal_schemas.PMSSignalOut])
def get_pms_signals(
    project_id: str,
    component: Optional[str] = Query(None, description="Filter by component name"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    status_filter: Optional[str] = Query(None, description="Filter by status", alias="status"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get PMS signals with optional filters"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    component_filter = [component] if component else None
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    
    return pms_signal_crud.get_pms_signals(
        db, project_id, component_filter, signal_type, status_filter, date_from_dt, date_to_dt
    )

@router.get("/signals/{signal_id}", response_model=pms_signal_schemas.PMSSignalOut)
def get_pms_signal(
    project_id: str,
    signal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a PMS signal by ID"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    signal = pms_signal_crud.get_pms_signal(db, signal_id, project_id)
    if not signal:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    return signal

@router.put("/signals/{signal_id}", response_model=pms_signal_schemas.PMSSignalOut)
def update_pms_signal(
    project_id: str,
    signal_id: str,
    signal_update: pms_signal_schemas.PMSSignalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a PMS signal"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    signal = pms_signal_crud.update_pms_signal(db, signal_id, project_id, signal_update)
    if not signal:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    return signal

@router.delete("/signals/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pms_signal(
    project_id: str,
    signal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a PMS signal"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = pms_signal_crud.delete_pms_signal(db, signal_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    return None

# Handoff Endpoints
@router.post("/signals/{signal_id}/link/risk-item")
def link_signal_to_risk_item(
    project_id: str,
    signal_id: str,
    request: pms_signal_schemas.PMSSignalLinkRiskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Link a PMS signal to a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify signal exists
    signal = pms_signal_crud.get_pms_signal(db, signal_id, project_id)
    if not signal:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    # Verify risk item exists (import needed)
    from crud import risk_item as risk_item_crud
    risk_item = risk_item_crud.get_risk_item(db, request.risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # Create trace link
    trace_link = trace_crud.create_trace_link(
        db,
        TraceLinkCreate(
            project_id=project_id,
            from_type="pms_signal",
            from_id=signal_id,
            to_type="risk_item",
            to_id=request.risk_item_id,
            link_type=request.link_type
        )
    )
    
    return {"message": "Signal linked to risk item", "trace_link_id": trace_link.id}

@router.post("/signals/{signal_id}/handoff/capa")
def handoff_signal_to_capa(
    project_id: str,
    signal_id: str,
    request: pms_signal_schemas.PMSSignalHandoffCAPARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create CAPA from PMS signal with automatic trace link (transactional, idempotent)"""
    endpoint = f"/projects/{project_id}/pms/signals/{signal_id}/handoff/capa"
    
    # Check idempotency
    if idempotency_key:
        cached_response = idempotency_crud.get_idempotent_response(
            db, idempotency_key, current_user.id, endpoint
        )
        if cached_response:
            return cached_response
    
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify signal exists
    signal = pms_signal_crud.get_pms_signal(db, signal_id, project_id)
    if not signal:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    try:
        # Build CAPA description with signal context
        signal_key = signal.signal_key
        title = request.capa_title or f"CAPA: Address {signal_key}"
        root_cause = f"Post-market signal {signal_key}: {signal.title}\n\n{signal.description or ''}"
        if signal.recommended_action:
            root_cause += f"\n\nRecommended Action: {signal.recommended_action}"
        
        # Create CAPA
        capa = capa_schemas.CAPACreate(
            project_id=project_id,
            root_cause=root_cause,
            capa_plan=request.capa_description or f"Implement corrective actions to address signal {signal_key}",
            effectiveness_check="Monitor post-market data to verify signal resolution"
        )
        created_capa = capa_crud.create_capa(db, capa)
        
        # Create trace link: pms_signal → capa
        trace_link = trace_crud.create_trace_link(
            db,
            TraceLinkCreate(
                project_id=project_id,
                from_type="pms_signal",
                from_id=signal_id,
                to_type="capa",
                to_id=created_capa.id,
                link_type="generated_from"
            )
        )
        
        # Create audit log event
        audit_log_crud.create_audit_log_event(
            db,
            AuditLogEventCreate(
                project_id=project_id,
                event_type="handoff.capa.created.from_pms",
                artifact_type="capa",
                artifact_id=created_capa.id,
                user_id=current_user.id,
                metadata={"pms_signal_id": signal_id, "signal_key": signal_key}
            )
        )
        
        # Cache idempotency response
        if idempotency_key:
            idempotency_crud.cache_idempotent_response(
                db, idempotency_key, current_user.id, endpoint, {"capa_id": created_capa.id, "trace_link_id": trace_link.id}
            )
        
        db.commit()
        return {"capa_id": created_capa.id, "trace_link_id": trace_link.id, "message": "CAPA created from PMS signal"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create CAPA: {str(e)}")

@router.post("/signals/{signal_id}/handoff/change")
def handoff_signal_to_change(
    project_id: str,
    signal_id: str,
    request: pms_signal_schemas.PMSSignalHandoffChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create Change Control from PMS signal with automatic trace link (transactional, idempotent)"""
    endpoint = f"/projects/{project_id}/pms/signals/{signal_id}/handoff/change"
    
    # Check idempotency
    if idempotency_key:
        cached_response = idempotency_crud.get_idempotent_response(
            db, idempotency_key, current_user.id, endpoint
        )
        if cached_response:
            return cached_response
    
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify signal exists
    signal = pms_signal_crud.get_pms_signal(db, signal_id, project_id)
    if not signal:
        raise HTTPException(status_code=404, detail="PMS signal not found")
    
    try:
        # Build change description with signal context
        signal_key = signal.signal_key
        title = request.change_title or f"Change: Address {signal_key}"
        change_summary = f"Post-market signal {signal_key}: {signal.title}\n\n{signal.description or ''}"
        if signal.recommended_action:
            change_summary += f"\n\nRecommended Action: {signal.recommended_action}"
        
        # Create Change Control
        change = cc_schemas.ChangeControlCreate(
            project_id=project_id,
            change_summary=change_summary,
            change_description=request.change_description or f"Implement changes to address signal {signal_key}",
            change_type="corrective"
        )
        created_change = cc_crud.create_change_control(db, change, current_user.id)
        
        # Create trace link: pms_signal → change_control
        trace_link = trace_crud.create_trace_link(
            db,
            TraceLinkCreate(
                project_id=project_id,
                from_type="pms_signal",
                from_id=signal_id,
                to_type="change_control",
                to_id=created_change.id,
                link_type="generated_from"
            )
        )
        
        # Create audit log event
        audit_log_crud.create_audit_log_event(
            db,
            AuditLogEventCreate(
                project_id=project_id,
                event_type="handoff.change.created.from_pms",
                artifact_type="change_control",
                artifact_id=created_change.id,
                user_id=current_user.id,
                metadata={"pms_signal_id": signal_id, "signal_key": signal_key}
            )
        )
        
        # Cache idempotency response
        if idempotency_key:
            idempotency_crud.cache_idempotent_response(
                db, idempotency_key, current_user.id, endpoint, {"change_id": created_change.id, "trace_link_id": trace_link.id}
            )
        
        db.commit()
        return {"change_id": created_change.id, "trace_link_id": trace_link.id, "message": "Change Control created from PMS signal"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create Change Control: {str(e)}")

# Report Endpoints
@router.post("/reports/signal-feedback/generate")
def generate_pms_signal_feedback_report(
    project_id: str,
    request: pms_signal_schemas.PMSSignalReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate PMS Signal Feedback Report"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse date range
    date_from = datetime.fromisoformat(request.date_from) if request.date_from else None
    date_to = datetime.fromisoformat(request.date_to) if request.date_to else None
    
    # Build evidence
    evidence = pms_signal_report_builder.build_pms_signal_feedback_evidence(
        db=db,
        project_id=project_id,
        component_filter=request.components,
        date_from=date_from,
        date_to=date_to,
        include_open_only=request.include_open_only,
        include_traceability=request.include_traceability,
        include_actions=request.include_actions
    )
    
    # Render HTML
    pms_report_html = pms_signal_report_renderer.render_pms_signal_feedback_html(evidence, project.name)
    
    return {
        "project_id": project_id,
        "components": request.components or [],
        "generated_at": datetime.now().isoformat(),
        "pms_report_html": pms_report_html,
        "counts": evidence.get("summary", {}),
        "summary": evidence.get("summary", {})
    }

@router.get("/reports/signal-feedback/export", response_class=HTMLResponse)
def export_pms_signal_feedback_report(
    project_id: str,
    components: Optional[str] = Query(None, description="Comma-separated component names"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    include_open_only: bool = Query(False, description="Include only open signals"),
    include_traceability: bool = Query(True, description="Include traceability"),
    include_actions: bool = Query(True, description="Include actions"),
    format: str = Query("html", description="Export format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export PMS Signal Feedback Report as HTML"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse component filter
    component_filter = None
    if components:
        component_names = [name.strip() for name in components.split(",")]
        component_filter = [{"name": name} for name in component_names]
    
    # Parse date range
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    
    # Build evidence
    evidence = pms_signal_report_builder.build_pms_signal_feedback_evidence(
        db=db,
        project_id=project_id,
        component_filter=component_filter,
        date_from=date_from_dt,
        date_to=date_to_dt,
        include_open_only=include_open_only,
        include_traceability=include_traceability,
        include_actions=include_actions
    )
    
    # Render HTML
    pms_report_html = pms_signal_report_renderer.render_pms_signal_feedback_html(evidence, project.name)
    
    return HTMLResponse(content=pms_report_html)

