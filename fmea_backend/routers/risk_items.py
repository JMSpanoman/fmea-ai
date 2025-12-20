from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import risk_item as risk_item_schemas
from crud import risk_item as risk_item_crud
from crud import risk_item_version as version_crud
from crud import risk_control as control_crud
from crud import project as project_crud
from crud import approval_phase3 as approval_crud
from crud import traceability as trace_crud
from crud import ai_event as ai_event_crud
from crud import design_control as dc_crud
from crud import vv as vv_crud
from crud import capa as capa_crud
from crud import change_control_phase3 as cc_crud
from crud import audit_log_event as audit_log_crud
from crud import idempotency as idempotency_crud
from schemas import ai_event as ai_event_schemas
from schemas import design_control as dc_schemas
from schemas import vv as vv_schemas
from schemas import capa as capa_schemas
from schemas import change_control as cc_schemas
from schemas.trace import TraceLinkCreate
from schemas.audit_log_event import AuditLogEventCreate
from typing import List, Optional
import uuid

router = APIRouter(prefix="/projects/{project_id}", tags=["Risk Items"])

@router.get("/risk-items", response_model=List[risk_item_schemas.RiskItemOut])
def get_risk_items(
    project_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all risk items for a project, optionally filtered by status or category"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Apply filters if provided
    if status:
        risk_items = risk_item_crud.get_risk_items_by_status(db, project_id, status)
    elif category:
        risk_items = risk_item_crud.get_risk_items_by_category(db, project_id, category)
    else:
        risk_items = risk_item_crud.get_risk_items_by_project(db, project_id)
    
    return risk_items

@router.post("/risk-items", response_model=risk_item_schemas.RiskItemOut, status_code=status.HTTP_201_CREATED)
def create_risk_item(
    project_id: str,
    risk_item: risk_item_schemas.RiskItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new risk item"""
    # Verify project belongs to user and matches path parameter
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(risk_item, 'model_copy'):
        risk_item = risk_item.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        risk_item_dict = risk_item.dict() if hasattr(risk_item, 'dict') else risk_item.model_dump()
        risk_item_dict['project_id'] = project_id
        risk_item = risk_item_schemas.RiskItemCreate(**risk_item_dict)
    
    return risk_item_crud.create_risk_item(db, risk_item)

@router.get("/risk-items/{risk_item_id}", response_model=risk_item_schemas.RiskItemOut)
def get_risk_item(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return risk_item

@router.put("/risk-items/{risk_item_id}", response_model=risk_item_schemas.RiskItemOut)
def update_risk_item(
    project_id: str,
    risk_item_id: str,
    risk_item: risk_item_schemas.RiskItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a risk item (creates new version under the hood for ISO 14971 compliance)"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_risk_item = risk_item_crud.update_risk_item(
        db, risk_item_id, risk_item, project_id, changed_by=current_user.id
    )
    if not updated_risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return updated_risk_item

@router.post("/risk-items/{risk_item_id}/versions", response_model=risk_item_schemas.RiskItemVersionOut, status_code=status.HTTP_201_CREATED)
def create_risk_item_version(
    project_id: str,
    risk_item_id: str,
    version_data: risk_item_schemas.RiskItemVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Explicitly create a new version of a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    version = version_crud.create_risk_item_version(
        db, risk_item_id, version_data, changed_by=current_user.id
    )
    return version

@router.get("/risk-items/{risk_item_id}/versions", response_model=List[risk_item_schemas.RiskItemVersionOut])
def get_risk_item_versions(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all versions for a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    return version_crud.get_risk_item_versions(db, risk_item_id)

@router.get("/risk-items/{risk_item_id}/versions/{version_id}", response_model=risk_item_schemas.RiskItemVersionOut)
def get_risk_item_version(
    project_id: str,
    risk_item_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific version of a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    version = version_crud.get_risk_item_version(db, version_id, risk_item_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version

@router.delete("/risk-items/{risk_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_item(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = risk_item_crud.delete_risk_item(db, risk_item_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk item not found")
    return None

# Risk Control endpoints
@router.post("/risk-items/{risk_item_id}/controls", response_model=risk_item_schemas.RiskControlOut, status_code=status.HTTP_201_CREATED)
def create_risk_control(
    project_id: str,
    risk_item_id: str,
    control: risk_item_schemas.RiskControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new risk control for a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # Ensure risk_item_id and project_id match
    if hasattr(control, 'model_copy'):
        control = control.model_copy(update={'risk_item_id': risk_item_id, 'project_id': project_id})
    else:
        control_dict = control.dict() if hasattr(control, 'dict') else control.model_dump()
        control_dict['risk_item_id'] = risk_item_id
        control_dict['project_id'] = project_id
        control = risk_item_schemas.RiskControlCreate(**control_dict)
    
    return control_crud.create_risk_control(db, control)

@router.get("/risk-items/{risk_item_id}/controls", response_model=List[risk_item_schemas.RiskControlOut])
def get_risk_controls(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all risk controls for a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    return control_crud.get_risk_controls_by_risk_item(db, risk_item_id)

@router.get("/risk-items/{risk_item_id}/controls/{control_id}", response_model=risk_item_schemas.RiskControlOut)
def get_risk_control(
    project_id: str,
    risk_item_id: str,
    control_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific risk control"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    control = control_crud.get_risk_control(db, control_id, risk_item_id)
    if not control:
        raise HTTPException(status_code=404, detail="Risk control not found")
    return control

@router.patch("/risk-items/{risk_item_id}/controls/{control_id}", response_model=risk_item_schemas.RiskControlOut)
def update_risk_control(
    project_id: str,
    risk_item_id: str,
    control_id: str,
    control: risk_item_schemas.RiskControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a risk control"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_control = control_crud.update_risk_control(db, control_id, control, risk_item_id)
    if not updated_control:
        raise HTTPException(status_code=404, detail="Risk control not found")
    return updated_control

@router.delete("/risk-items/{risk_item_id}/controls/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_control(
    project_id: str,
    risk_item_id: str,
    control_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a risk control"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = control_crud.delete_risk_control(db, control_id, risk_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Risk control not found")
    return None

# Approval endpoint
@router.post("/risk-items/{risk_item_id}/approve", status_code=status.HTTP_201_CREATED)
def approve_risk_item_version(
    project_id: str,
    risk_item_id: str,
    approval_request: risk_item_schemas.RiskItemApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject a specific risk item version"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # Verify version exists and belongs to risk item
    version = version_crud.get_risk_item_version(db, approval_request.version_id, risk_item_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Create approval record
    from schemas.approval import ApprovalCreate
    approval = ApprovalCreate(
        artifact_type="risk_item_version",
        artifact_id=approval_request.version_id,
        approver_id=current_user.id,
        status=approval_request.decision,
        comment=f"{approval_request.rationale}\n\n{approval_request.comment or ''}"
    )
    
    created_approval = approval_crud.create_approval(db, approval)
    return {"message": f"Version {approval_request.decision}", "approval_id": created_approval.id}

# Traceability endpoints
@router.get("/risk-items/{risk_item_id}/links")
def get_risk_item_links(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trace links for a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # Get links where risk_item is the source
    links = trace_crud.get_trace_links_from(db, "risk_item", risk_item_id, project_id)
    # Also get links where risk_item is the target
    links_to = trace_crud.get_trace_links_to(db, "risk_item", risk_item_id, project_id)
    
    return {"from": links, "to": links_to}

@router.post("/risk-items/{risk_item_id}/links", status_code=status.HTTP_201_CREATED)
def create_risk_item_link(
    project_id: str,
    risk_item_id: str,
    link: dict,  # {to_type: str, to_id: str}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a trace link from a risk item to another artifact"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    from schemas.trace import TraceLinkCreate
    link_create = TraceLinkCreate(
        project_id=project_id,
        from_type="risk_item",
        from_id=risk_item_id,
        to_type=link.get("to_type"),
        to_id=link.get("to_id")
    )
    
    created_link = trace_crud.create_trace_link(db, link_create)
    return created_link

# AI Risk Suggestions endpoint
@router.post("/risk-items/{risk_item_id}/ai/suggest")
async def suggest_risk_assessment(
    project_id: str,
    risk_item_id: str,
    request: dict,  # { hazard, hazardous_situation, harm }
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions for risk assessment"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify risk item exists and belongs to project
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # TODO: Call actual AI service (OpenAI, etc.)
    # For now, return mock suggestions
    suggestions = {
        "severity": 7,
        "probability_of_harm": 5,
        "detection": 3,
        "risk_score": 105,
        "risk_level": "High",
        "mitigation": "Implement protective controls",
        "residual_severity": 5,
        "residual_probability_of_harm": 3,
        "residual_detection": 2,
        "residual_risk_score": 30,
        "residual_risk_level": "Medium"
    }
    
    # Log AI event
    ai_event = ai_event_crud.create_ai_event(
        db,
        ai_event_schemas.AIEventCreate(
            project_id=project_id,
            context_type="risk_item",
            context_id=risk_item_id,
            prompt_name="risk_suggest",
            input_summary=f"Hazard: {request.get('hazard', '')[:100]}",
            output_json=suggestions
        ),
        current_user.id
    )
    
    return {
        "suggestions": suggestions,
        "ai_event_id": ai_event.id
    }

# AI Event Disposition endpoint
@router.patch("/ai/events/{event_id}/disposition")
def update_ai_event_disposition(
    event_id: str,
    update_data: ai_event_schemas.AIEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update AI event disposition"""
    updated_event = ai_event_crud.update_ai_event_disposition(
        db, event_id, update_data, current_user.id
    )
    if not updated_event:
        raise HTTPException(status_code=404, detail="AI event not found")
    return updated_event

# Get AI events for a risk item
@router.get("/risk-items/{risk_item_id}/ai/events")
def get_risk_item_ai_events(
    project_id: str,
    risk_item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI event history for a risk item"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    events = ai_event_crud.get_ai_events_by_context(
        db, project_id, "risk_item", risk_item_id
    )
    return events

# Handoff Actions - Cross-module connectivity
# Canonical link types enforced via schemas.trace enums

# Risk Control → Design Handoff
@router.post("/risk-items/{risk_item_id}/controls/{control_id}/handoff/design")
def handoff_control_to_design(
    project_id: str,
    risk_item_id: str,
    control_id: str,
    request: dict,  # { target_type: "design_input"|"design_output"|"vv_test", name: str, description: str, ... }
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create Design artifact from Risk Control with automatic trace link (transactional, idempotent)"""
    endpoint = f"/risk-items/{risk_item_id}/controls/{control_id}/handoff/design"
    
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
    
    # Verify risk item and control exist
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    control = control_crud.get_risk_control(db, control_id, risk_item_id)
    if not control:
        raise HTTPException(status_code=404, detail="Risk control not found")
    
    target_type = request.get("target_type")
    if target_type not in ["design_input", "design_output", "vv_test"]:
        raise HTTPException(status_code=400, detail="Invalid target_type. Must be design_input, design_output, or vv_test")
    
    # Build description with risk context
    risk_key = risk_item.title or risk_item.id[:8]
    control_key = control.control_name or control.id[:8]
    base_description = f"{request.get('description', '')}\n\nMitigates risk {risk_key} via control {control_key}."
    
    created_artifact = None
    trace_link_to_type = None
    trace_link = None
    
    # Transactional: both artifact and link must succeed
    try:
        # Create the artifact based on target_type
        if target_type == "design_input":
            design_input = dc_schemas.DesignInputCreate(
                project_id=project_id,
                text=base_description,
                source="user",
                linked_risk_ids=[risk_item_id]
            )
            created_artifact = dc_crud.create_design_input(db, design_input)
            trace_link_to_type = "design_input"
            
        elif target_type == "design_output":
            design_output = dc_schemas.DesignOutputCreate(
                project_id=project_id,
                text=base_description,
                source="user"
            )
            created_artifact = dc_crud.create_design_output(db, design_output)
            trace_link_to_type = "design_output"
            
        elif target_type == "vv_test":
            # V&V tests require design_output_id
            design_output_id = request.get("design_output_id")
            if not design_output_id:
                raise HTTPException(status_code=400, detail="design_output_id required for vv_test")
            
            vv_test = vv_schemas.VVTestCreate(
                project_id=project_id,
                design_output_id=design_output_id,
                test_method=request.get("test_method", "Verification test"),
                acceptance_criteria=request.get("acceptance_criteria", "Control effectiveness verified"),
                rationale=base_description
            )
            created_artifact = vv_crud.create_vv_test(db, vv_test)
            trace_link_to_type = "vv_test"
        
        # Create trace link: risk_control → artifact (using canonical enum)
        trace_link = trace_crud.create_trace_link(
            db,
            TraceLinkCreate(
                project_id=project_id,
                from_type="risk_control",
                from_id=control_id,
                to_type=trace_link_to_type,
                to_id=created_artifact.id,
                link_type="verified_by" if target_type == "vv_test" else "traces_to"
            )
        )
        
        # Create audit log event
        audit_log_crud.create_audit_log_event(
            db,
            AuditLogEventCreate(
                project_id=project_id,
                user_id=current_user.id,
                event_type=f"handoff.design.{target_type}.created",
                details_json={
                    "risk_item_id": risk_item_id,
                    "risk_key": risk_key,
                    "control_id": control_id,
                    "control_key": control_key,
                    "created_artifact_id": created_artifact.id,
                    "artifact_type": target_type,
                    "trace_link_id": trace_link.id
                }
            )
        )
        
        response = {
            "created_artifact": created_artifact,
            "trace_link": trace_link,
            "message": f"Created {target_type} and linked from risk control"
        }
        
        # Store for idempotency
        if idempotency_key:
            idempotency_crud.store_idempotent_response(
                db, idempotency_key, current_user.id, project_id,
                endpoint, response
            )
        
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create handoff: {str(e)}")

# Handoff: Risk Item → CAPA
@router.post("/risk-items/{risk_item_id}/handoff/capa")
def handoff_risk_to_capa(
    project_id: str,
    risk_item_id: str,
    request: dict,  # { title: str, priority: str, ... }
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create CAPA from Risk Item with automatic trace link (transactional, idempotent)"""
    endpoint = f"/risk-items/{risk_item_id}/handoff/capa"
    
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
    
    # Verify risk item exists
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    # Get current version for context
    current_version = version_crud.get_current_version(db, risk_item_id)
    
    # Build problem statement with risk chain
    risk_key = risk_item.title or risk_item.id[:8]
    
    # Build root cause with title if provided
    title = request.get("title", f"CAPA: Mitigate {risk_key}")
    root_cause_base = title
    if current_version:
        if current_version.hazard:
            root_cause_base += f"\n\nHazard: {current_version.hazard}"
        if current_version.hazardous_situation:
            root_cause_base += f"\nHazardous Situation: {current_version.hazardous_situation}"
        if current_version.harm:
            root_cause_base += f"\nHarm: {current_version.harm}"
        if current_version.risk_rationale:
            root_cause_base += f"\n\nRationale: {current_version.risk_rationale}"
    
    # If user provided root_cause, prepend title
    root_cause = request.get("root_cause") or root_cause_base
    if request.get("root_cause") and root_cause_base != request.get("root_cause"):
        root_cause = f"{title}\n\n{root_cause}"
    
    try:
        # Create CAPA
        capa = capa_schemas.CAPACreate(
            project_id=project_id,
            root_cause=root_cause,
            capa_plan=request.get("capa_plan", f"Implement controls to mitigate {risk_key}"),
            effectiveness_check=request.get("effectiveness_check", "Verify risk reduction through monitoring"),
            linked_risk_ids=[risk_item_id]
        )
        created_capa = capa_crud.create_capa(db, capa)
        
        # Create trace link: risk_item → capa (transactional)
        trace_link = trace_crud.create_trace_link(
            db,
            TraceLinkCreate(
                project_id=project_id,
                from_type="risk_item",
                from_id=risk_item_id,
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
                user_id=current_user.id,
                event_type="handoff.capa.created",
                details_json={
                    "risk_item_id": risk_item_id,
                    "risk_key": risk_key,
                    "version_id": current_version.id if current_version else None,
                    "created_artifact_id": created_capa.id,
                    "trace_link_id": trace_link.id
                }
            )
        )
        
        response = {
            "created_artifact": created_capa,
            "trace_link": trace_link,
            "message": "Created CAPA and linked from risk item"
        }
        
        # Store for idempotency
        if idempotency_key:
            idempotency_crud.store_idempotent_response(
                db, idempotency_key, current_user.id, project_id,
                endpoint, response
            )
        
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create CAPA: {str(e)}")

# Handoff: Risk Item Version → Change Control
@router.post("/risk-items/{risk_item_id}/handoff/change")
def handoff_risk_version_to_change(
    project_id: str,
    risk_item_id: str,
    request: dict,  # { version_id: str, change_summary: str, ... }
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create Change Control from Risk Item Version with automatic trace link (transactional, idempotent)"""
    endpoint = f"/risk-items/{risk_item_id}/handoff/change"
    
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
    
    # Verify risk item exists
    risk_item = risk_item_crud.get_risk_item(db, risk_item_id, project_id)
    if not risk_item:
        raise HTTPException(status_code=404, detail="Risk item not found")
    
    version_id = request.get("version_id")
    if not version_id:
        # Use current version if not specified
        current_version = version_crud.get_current_version(db, risk_item_id)
        if not current_version:
            raise HTTPException(status_code=404, detail="No version found")
        version_id = current_version.id
    else:
        # Verify version exists
        version = version_crud.get_risk_item_version(db, version_id, risk_item_id)
        if not version:
            raise HTTPException(status_code=404, detail="Version not found")
    
    version = version_crud.get_risk_item_version(db, version_id, risk_item_id)
    risk_key = risk_item.title or risk_item.id[:8]
    
    # Get impacted artifacts from trace links
    links = trace_crud.get_trace_links_from(db, "risk_item", risk_item_id, project_id)
    impacted_artifacts = []
    for link in links:
        impacted_artifacts.append(f"{link.to_type}: {link.to_id[:8]}...")
    
    # Build change summary from diff or version info
    change_summary = request.get("change_summary") or f"Risk update: {risk_key} v{version.version_number}"
    if version.change_summary:
        change_summary += f"\n\nChanges: {version.change_summary}"
    
    if impacted_artifacts:
        change_summary += f"\n\nImpacted artifacts: {', '.join(impacted_artifacts)}"
    
    try:
        # Create Change Control
        change_control = cc_schemas.ChangeControlCreate(
            project_id=project_id,
            title=request.get("title", f"Change: {risk_key} v{version.version_number}"),
            description=change_summary,
            reason=f"Risk update: {risk_key} v{version.version_number}",
            status="open",
            linked_risk_ids=[risk_item_id]
        )
        created_change = cc_crud.create_change_control(db, change_control)
        
        # Create trace link: risk_item_version → change_control (transactional)
        trace_link = trace_crud.create_trace_link(
            db,
            TraceLinkCreate(
                project_id=project_id,
                from_type="risk_item_version",
                from_id=version_id,
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
                user_id=current_user.id,
                event_type="handoff.change.created",
                details_json={
                    "risk_item_id": risk_item_id,
                    "risk_key": risk_key,
                    "version_id": version_id,
                    "version_number": version.version_number,
                    "created_artifact_id": created_change.id,
                    "trace_link_id": trace_link.id
                }
            )
        )
        
        response = {
            "created_artifact": created_change,
            "trace_link": trace_link,
            "message": "Created Change Control and linked from risk version"
        }
        
        # Store for idempotency
        if idempotency_key:
            idempotency_crud.store_idempotent_response(
                db, idempotency_key, current_user.id, project_id,
                endpoint, response
            )
        
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create Change Control: {str(e)}")

