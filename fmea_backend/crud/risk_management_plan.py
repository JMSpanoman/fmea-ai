from sqlalchemy.orm import Session
from models.risk_management_plan import RiskManagementPlan
from schemas.risk_management_plan import RMPGenerateRequest, RMPUpdateRequest
from typing import List, Optional
import uuid
import json
from datetime import datetime, timezone

def create_rmp(
    db: Session,
    project_id: str,
    rmp_data: RMPGenerateRequest,
    rendered_html: str,
    created_by: str,
    acceptability_criteria_json: str,
    risk_methodology: str,
    review_roles_json: str,
    risk_control_categories_json: str,
    benefit_risk_criteria: str,
    lifecycle_linkage: str,
    governance_rules: str
) -> RiskManagementPlan:
    """Create a new Risk Management Plan"""
    # Generate title if not provided
    title = rmp_data.title or f"Risk Management Plan – {project_id}"
    
    # Convert components to JSON
    components_json = json.dumps([comp.dict() for comp in rmp_data.components])
    
    db_rmp = RiskManagementPlan(
        id=str(uuid.uuid4()),
        project_id=project_id,
        title=title,
        scope=rmp_data.scope,
        intended_use=rmp_data.intended_use,
        components_json=components_json,
        acceptability_criteria_json=acceptability_criteria_json,
        risk_methodology=risk_methodology,
        review_roles_json=review_roles_json,
        risk_control_categories_json=risk_control_categories_json,
        benefit_risk_criteria=benefit_risk_criteria,
        lifecycle_linkage=lifecycle_linkage,
        governance_rules=governance_rules,
        rendered_html=rendered_html,
        status='draft',
        current_version_no=1,
        created_by=created_by
    )
    db.add(db_rmp)
    db.commit()
    db.refresh(db_rmp)
    return db_rmp

def get_rmp_by_project(db: Session, project_id: str) -> Optional[RiskManagementPlan]:
    """Get the current RMP for a project (most recent)"""
    return db.query(RiskManagementPlan).filter(
        RiskManagementPlan.project_id == project_id
    ).order_by(RiskManagementPlan.created_at.desc()).first()

def get_rmp(db: Session, rmp_id: str, project_id: str) -> Optional[RiskManagementPlan]:
    """Get a specific RMP"""
    return db.query(RiskManagementPlan).filter(
        RiskManagementPlan.id == rmp_id,
        RiskManagementPlan.project_id == project_id
    ).first()

def update_rmp(
    db: Session,
    rmp_id: str,
    project_id: str,
    rmp_update: RMPUpdateRequest,
    rendered_html: Optional[str] = None
) -> Optional[RiskManagementPlan]:
    """Update an RMP (creates new version)"""
    db_rmp = get_rmp(db, rmp_id, project_id)
    if not db_rmp:
        return None
    
    # Update fields
    if rmp_update.title is not None:
        db_rmp.title = rmp_update.title
    if rmp_update.scope is not None:
        db_rmp.scope = rmp_update.scope
    if rmp_update.intended_use is not None:
        db_rmp.intended_use = rmp_update.intended_use
    if rmp_update.components is not None:
        db_rmp.components_json = json.dumps([comp.dict() for comp in rmp_update.components])
    if rmp_update.acceptability_criteria_json is not None:
        db_rmp.acceptability_criteria_json = rmp_update.acceptability_criteria_json
    if rmp_update.review_roles is not None:
        db_rmp.review_roles_json = json.dumps(rmp_update.review_roles)
    
    # Update rendered HTML if provided
    if rendered_html is not None:
        db_rmp.rendered_html = rendered_html
    
    # Increment version
    db_rmp.current_version_no += 1
    db_rmp.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_rmp)
    return db_rmp

def approve_rmp(db: Session, rmp_id: str, project_id: str) -> Optional[RiskManagementPlan]:
    """Approve an RMP (changes status to approved)"""
    db_rmp = get_rmp(db, rmp_id, project_id)
    if not db_rmp:
        return None
    
    if db_rmp.status != "approved":
        db_rmp.status = "approved"
        db.commit()
        db.refresh(db_rmp)
    
    return db_rmp

def get_all_rmps_by_project(db: Session, project_id: str) -> List[RiskManagementPlan]:
    """Get all RMPs for a project"""
    return db.query(RiskManagementPlan).filter(
        RiskManagementPlan.project_id == project_id
    ).order_by(RiskManagementPlan.created_at.desc()).all()

