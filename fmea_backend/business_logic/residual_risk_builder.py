"""
Business Logic for Residual Risk Evaluation Evidence Builder
Builds residual risk evaluation data from SmartQS risk_item_versions
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.approval import Approval
from models.component import Component
from models.risk_management_plan import RiskManagementPlan
from sqlalchemy import or_
import json

def get_acceptability_thresholds(
    db: Session,
    project_id: str,
    custom_thresholds: Optional[Dict[str, Any]] = None,
    acceptability_profile: str = "default_med_device"
) -> Dict[str, Any]:
    """
    Get acceptability thresholds from custom, RMP, or defaults
    
    Priority:
    1. custom_thresholds from request
    2. RMP stored thresholds
    3. Default system thresholds
    """
    if custom_thresholds:
        return custom_thresholds
    
    # Try to get from RMP
    rmp = db.query(RiskManagementPlan).filter(
        RiskManagementPlan.project_id == project_id
    ).order_by(RiskManagementPlan.created_at.desc()).first()
    
    if rmp:
        try:
            criteria = json.loads(rmp.acceptability_criteria_json)
            thresholds = criteria.get("thresholds", {})
            if thresholds:
                return thresholds
        except:
            pass
    
    # Default thresholds
    return {
        "Low": {"min": 1, "max": 7, "acceptability": "acceptable"},
        "Medium": {"min": 8, "max": 19, "acceptability": "acceptable_with_justification"},
        "High": {"min": 20, "max": 59, "acceptability": "needs_benefit_risk"},
        "Critical": {"min": 60, "max": 100, "acceptability": "unacceptable"}
    }

def infer_residual_acceptability(
    residual_risk_score: Optional[int],
    thresholds: Dict[str, Any]
) -> tuple[str, str]:
    """
    Infer residual acceptability from score using thresholds
    
    Returns:
        (acceptability_level, acceptability_value)
    """
    if residual_risk_score is None:
        return ("unknown", "unknown")
    
    # Check thresholds in order: Critical, High, Medium, Low
    for level in ["Critical", "High", "Medium", "Low"]:
        threshold = thresholds.get(level, {})
        min_score = threshold.get("min", 0)
        max_score = threshold.get("max", 100)
        if min_score <= residual_risk_score <= max_score:
            return (level.lower(), threshold.get("acceptability", "unknown"))
    
    return ("unknown", "unknown")

def build_residual_risk_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    version_scope: str = "approved_only",
    include_unapproved: bool = False,
    custom_thresholds: Optional[Dict[str, Any]] = None,
    acceptability_profile: str = "default_med_device"
) -> Dict[str, Any]:
    """
    Build residual risk evaluation evidence from SmartQS risk_item_versions
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"id": "...", "name": "..."}]
        version_scope: "approved_only", "current", or "all"
        include_unapproved: If True, include unapproved versions even when version_scope is approved_only
        custom_thresholds: Custom acceptability thresholds
        acceptability_profile: Profile name for thresholds
    
    Returns:
        Dictionary with residual risk evaluation data
    """
    # Get acceptability thresholds
    thresholds = get_acceptability_thresholds(db, project_id, custom_thresholds, acceptability_profile)
    
    # Extract component IDs and names from filter
    component_ids = []
    component_names = []
    if component_filter:
        for comp in component_filter:
            if comp.get("id"):
                component_ids.append(comp["id"])
            if comp.get("name"):
                component_names.append(comp["name"])
    
    # Query risk items filtered by components
    risk_items_query = db.query(RiskItem).filter(RiskItem.project_id == project_id)
    
    if component_ids or component_names:
        # Filter by component_id or component_name
        filters = []
        if component_ids:
            filters.append(RiskItem.component_id.in_(component_ids))
        if component_names:
            filters.append(RiskItem.component_name.in_(component_names))
        if filters:
            risk_items_query = risk_items_query.filter(or_(*filters))
    
    risk_items = risk_items_query.all()
    
    # Build residual risk rows
    residual_risk_rows = []
    versions_included = 0
    missing_residual_fields = 0
    missing_field_list = []
    
    for risk_item in risk_items:
        # Get all versions
        all_versions = db.query(RiskItemVersion).filter(
            RiskItemVersion.risk_item_id == risk_item.id
        ).order_by(RiskItemVersion.version_number.desc()).all()
        
        # Get current version
        current_version = None
        if risk_item.current_version_id:
            current_version = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        
        # Determine which versions to include
        versions_to_include = []
        
        if version_scope == "approved_only":
            # Get approved versions
            for version in all_versions:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == version.id,
                    Approval.status == "approved"
                ).all()
                if approvals:
                    versions_to_include.append((version, approvals[0]))
                elif include_unapproved:
                    versions_to_include.append((version, None))
        
        elif version_scope == "current":
            if current_version:
                # Check if current version is approved
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == current_version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((current_version, approvals[0] if approvals else None))
        
        elif version_scope == "all":
            # Include all versions
            for version in all_versions:
                approvals = db.query(Approval).filter(
                    Approval.artifact_type == "risk_item_version",
                    Approval.artifact_id == version.id,
                    Approval.status == "approved"
                ).all()
                versions_to_include.append((version, approvals[0] if approvals else None))
        
        # Build residual risk rows for included versions
        for version, approval in versions_to_include:
            # Get component name
            component_name = None
            if risk_item.component_id:
                component = db.query(Component).filter(Component.id == risk_item.component_id).first()
                if component:
                    component_name = component.name
            if not component_name:
                component_name = risk_item.component_name or "Unknown"
            
            # Extract residual fields
            residual_severity = version.residual_severity
            residual_probability = version.residual_probability_of_harm
            residual_risk_score = version.residual_risk_score
            
            # Compute residual_risk_score if missing but severity/probability exist
            if residual_risk_score is None and residual_severity is not None and residual_probability is not None:
                residual_risk_score = residual_severity * residual_probability
            
            # Check for missing fields
            has_missing_fields = (
                residual_severity is None or
                residual_probability is None or
                residual_risk_score is None
            )
            
            if has_missing_fields:
                missing_residual_fields += 1
                missing_field_list.append({
                    "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                    "version_id": version.id,
                    "version_no": version.version_number
                })
            
            # Determine residual acceptability
            # Check if stored (we don't have a residual_risk_acceptability field, so we'll infer)
            residual_acceptability_stored = None  # If you add this field later, check it here
            acceptability_source = "inferred"
            
            if residual_acceptability_stored:
                residual_acceptability = residual_acceptability_stored
                acceptability_source = "stored"
            else:
                # Infer from thresholds
                level, value = infer_residual_acceptability(residual_risk_score, thresholds)
                residual_acceptability = value
                acceptability_source = "inferred"
            
            row = {
                "risk_item_id": risk_item.id,
                "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                "version_id": version.id,
                "version_no": version.version_number,
                "component_name": component_name,
                "residual_severity": residual_severity,
                "residual_probability_of_harm": residual_probability,
                "residual_risk_score": residual_risk_score,
                "residual_acceptability": residual_acceptability,
                "acceptability_source": acceptability_source,
                "approved": approval is not None,
                "approved_at": approval.timestamp.isoformat() if approval and approval.timestamp else None,
                "approved_by": approval.approver_id if approval else None,
                "is_current": version.id == (current_version.id if current_version else None)
            }
            
            residual_risk_rows.append(row)
            versions_included += 1
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "version_scope": version_scope,
        "include_unapproved": include_unapproved,
        "thresholds": thresholds,
        "rows": residual_risk_rows,
        "missing_field_list": missing_field_list,
        "counts": {
            "versions_included": versions_included,
            "missing_residual_fields": missing_residual_fields
        }
    }

