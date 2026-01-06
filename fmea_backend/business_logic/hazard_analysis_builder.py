"""
Business Logic for Hazard Analysis Evidence Builder
Builds hazard analysis data from SmartQS risk_item_versions
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.approval import Approval
from models.component import Component
from sqlalchemy import or_

def build_hazard_analysis(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    version_scope: str = "approved_only",
    include_unapproved: bool = False
) -> Dict[str, Any]:
    """
    Build hazard analysis evidence from SmartQS risk_item_versions
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"id": "...", "name": "..."}]
        version_scope: "approved_only", "current", or "all"
        include_unapproved: If True, include unapproved versions even when version_scope is approved_only
    
    Returns:
        Dictionary with hazard analysis data
    """
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
    
    # Build hazard analysis rows
    hazard_analysis_rows = []
    risk_items_included = 0
    versions_included = 0
    unapproved_excluded = 0
    
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
                else:
                    unapproved_excluded += 1
        
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
        
        # Build hazard analysis rows for included versions
        for version, approval in versions_to_include:
            # Get component name
            component_name = None
            if risk_item.component_id:
                component = db.query(Component).filter(Component.id == risk_item.component_id).first()
                if component:
                    component_name = component.name
            if not component_name:
                component_name = risk_item.component_name or "Unknown"
            
            row = {
                "risk_item_id": risk_item.id,
                "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                "version_id": version.id,
                "version_no": version.version_number,
                "component_name": component_name,
                "hazard": version.hazard,
                "hazardous_situation": version.hazardous_situation,
                "harm": version.harm,
                "sequence_of_events": version.sequence_of_events,
                "failure_mode": version.failure_mode,
                "approved": approval is not None,
                "approved_at": approval.timestamp.isoformat() if approval and approval.timestamp else None,
                "approved_by": approval.approver_id if approval else None,
                "is_current": version.id == (current_version.id if current_version else None)
            }
            
            hazard_analysis_rows.append(row)
            versions_included += 1
        
        if versions_to_include:
            risk_items_included += 1
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "version_scope": version_scope,
        "include_unapproved": include_unapproved,
        "rows": hazard_analysis_rows,
        "counts": {
            "risk_items": risk_items_included,
            "versions_included": versions_included,
            "unapproved_excluded": unapproved_excluded
        }
    }

