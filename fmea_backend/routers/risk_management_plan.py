from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import risk_management_plan as rmp_schemas
from crud import risk_management_plan as rmp_crud
from crud import project as project_crud
from crud import approval_phase3 as approval_crud
from business_logic import rmp_generator
from datetime import datetime
import json

router = APIRouter(prefix="/projects/{project_id}", tags=["Risk Management Plan"])

@router.post("/risk-management-plan/generate", response_model=rmp_schemas.RMPOut, status_code=status.HTTP_201_CREATED)
def generate_rmp(
    project_id: str,
    rmp_request: rmp_schemas.RMPGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a new Risk Management Plan"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if RMP already exists
    existing_rmp = rmp_crud.get_rmp_by_project(db, project_id)
    if existing_rmp:
        raise HTTPException(
            status_code=400,
            detail="Risk Management Plan already exists for this project. Use PUT to update."
        )
    
    # Generate all required sections
    acceptability_criteria = rmp_generator.generate_acceptability_criteria(
        profile=rmp_request.acceptability_profile,
        custom=rmp_request.custom_acceptability_criteria
    )
    risk_methodology = rmp_generator.generate_risk_methodology()
    risk_control_categories = rmp_generator.generate_risk_control_categories()
    benefit_risk_criteria = rmp_generator.generate_benefit_risk_criteria()
    lifecycle_linkage = rmp_generator.generate_lifecycle_linkage()
    governance_rules = rmp_generator.generate_governance_rules()
    
    # Generate title if not provided
    title = rmp_request.title or f"Risk Management Plan – {project.name}"
    
    # Generate HTML
    rendered_html = rmp_generator.generate_rmp_html(
        title=title,
        scope=rmp_request.scope,
        intended_use=rmp_request.intended_use,
        components=rmp_request.components,
        acceptability_criteria=acceptability_criteria,
        risk_methodology=risk_methodology,
        review_roles=rmp_request.review_roles,
        risk_control_categories=risk_control_categories,
        benefit_risk_criteria=benefit_risk_criteria,
        lifecycle_linkage=lifecycle_linkage,
        governance_rules=governance_rules,
        version_no=1,
        created_at=datetime.now().isoformat()
    )
    
    # Convert to JSON strings
    acceptability_criteria_json = json.dumps(acceptability_criteria)
    review_roles_json = json.dumps(rmp_request.review_roles)
    risk_control_categories_json = json.dumps(risk_control_categories)
    
    # Create RMP
    rmp = rmp_crud.create_rmp(
        db=db,
        project_id=project_id,
        rmp_data=rmp_request,
        rendered_html=rendered_html,
        created_by=current_user.id,
        acceptability_criteria_json=acceptability_criteria_json,
        risk_methodology=risk_methodology,
        review_roles_json=review_roles_json,
        risk_control_categories_json=risk_control_categories_json,
        benefit_risk_criteria=benefit_risk_criteria,
        lifecycle_linkage=lifecycle_linkage,
        governance_rules=governance_rules
    )
    
    return rmp

@router.get("/risk-management-plan", response_model=rmp_schemas.RMPOut)
def get_rmp(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current Risk Management Plan for a project"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    rmp = rmp_crud.get_rmp_by_project(db, project_id)
    if not rmp:
        raise HTTPException(status_code=404, detail="Risk Management Plan not found")
    
    return rmp

@router.put("/risk-management-plan/{rmp_id}", response_model=rmp_schemas.RMPOut)
def update_rmp(
    project_id: str,
    rmp_id: str,
    rmp_update: rmp_schemas.RMPUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a Risk Management Plan (creates new version)"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get existing RMP
    existing_rmp = rmp_crud.get_rmp(db, rmp_id, project_id)
    if not existing_rmp:
        raise HTTPException(status_code=404, detail="Risk Management Plan not found")
    
    # Regenerate HTML if content changed
    rendered_html = None
    if (rmp_update.scope or rmp_update.intended_use or rmp_update.components or 
        rmp_update.acceptability_criteria_json or rmp_update.review_roles):
        
        # Parse existing data
        if rmp_update.components:
            components = rmp_update.components
        else:
            try:
                components = json.loads(existing_rmp.components_json)
            except:
                components = []
        
        if rmp_update.acceptability_criteria_json:
            acceptability_criteria = json.loads(rmp_update.acceptability_criteria_json)
        else:
            try:
                acceptability_criteria = json.loads(existing_rmp.acceptability_criteria_json)
            except:
                acceptability_criteria = {}
        
        if rmp_update.review_roles:
            review_roles = rmp_update.review_roles
        else:
            try:
                review_roles = json.loads(existing_rmp.review_roles_json)
            except:
                review_roles = {}
        
        # Parse risk control categories
        try:
            risk_control_categories = json.loads(existing_rmp.risk_control_categories_json)
        except:
            risk_control_categories = []
        
        # Regenerate HTML
        rendered_html = rmp_generator.generate_rmp_html(
            title=rmp_update.title or existing_rmp.title,
            scope=rmp_update.scope or existing_rmp.scope,
            intended_use=rmp_update.intended_use or existing_rmp.intended_use,
            components=components,
            acceptability_criteria=acceptability_criteria,
            risk_methodology=existing_rmp.risk_methodology,
            review_roles=review_roles,
            risk_control_categories=risk_control_categories,
            benefit_risk_criteria=existing_rmp.benefit_risk_criteria,
            lifecycle_linkage=existing_rmp.lifecycle_linkage,
            governance_rules=existing_rmp.governance_rules,
            version_no=existing_rmp.current_version_no + 1,
            created_at=datetime.now().isoformat()
        )
    
    # Update RMP
    updated_rmp = rmp_crud.update_rmp(
        db=db,
        rmp_id=rmp_id,
        project_id=project_id,
        rmp_update=rmp_update,
        rendered_html=rendered_html
    )
    
    if not updated_rmp:
        raise HTTPException(status_code=500, detail="Failed to update Risk Management Plan")
    
    return updated_rmp

@router.post("/risk-management-plan/{rmp_id}/approve", status_code=status.HTTP_200_OK)
def approve_rmp(
    project_id: str,
    rmp_id: str,
    approval_request: rmp_schemas.RMPApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a Risk Management Plan"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get RMP
    rmp = rmp_crud.get_rmp(db, rmp_id, project_id)
    if not rmp:
        raise HTTPException(status_code=404, detail="Risk Management Plan not found")
    
    # Create approval record
    from schemas.approval import ApprovalCreate
    approval = ApprovalCreate(
        artifact_type="risk_management_plan",
        artifact_id=rmp_id,
        approver_id=current_user.id,
        status=approval_request.decision,
        comment=approval_request.rationale
    )
    approval_crud.create_approval(db, approval)
    
    # Update RMP status if approved
    if approval_request.decision == "approved":
        rmp_crud.approve_rmp(db, rmp_id, project_id)
    
    return {
        "message": f"Risk Management Plan {approval_request.decision}",
        "rmp_id": rmp_id,
        "approval": approval
    }

@router.get("/risk-management-plan/{rmp_id}/export/html", response_class=HTMLResponse)
def export_rmp_html(
    project_id: str,
    rmp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export Risk Management Plan as HTML"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get RMP
    rmp = rmp_crud.get_rmp(db, rmp_id, project_id)
    if not rmp:
        raise HTTPException(status_code=404, detail="Risk Management Plan not found")
    
    return HTMLResponse(content=rmp.rendered_html)

