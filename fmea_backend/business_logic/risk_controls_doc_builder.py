"""
Business Logic for Risk Control Measures Documentation Evidence Builder
Builds risk control measures documentation from SmartQS risk_controls and trace_links
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_control import RiskControl
from models.risk_item_version import RiskItemVersion
from models.trace_link import TraceLink
from models.component import Component
from sqlalchemy import or_

def get_artifact_display(db: Session, artifact_type: str, artifact_id: str) -> str:
    """
    Get display label for an artifact (design_input, design_output, vv_test)
    """
    try:
        if artifact_type == "design_input":
            from models.design_input import DesignInput
            artifact = db.query(DesignInput).filter(DesignInput.id == artifact_id).first()
            if artifact:
                key = artifact.di_key or f"DI-{artifact.id[:8]}"
                title = artifact.title or artifact.requirement or artifact.text or 'Design Input'
                return f"{key} – {title}"
        elif artifact_type == "design_output":
            from models.design_output import DesignOutput
            artifact = db.query(DesignOutput).filter(DesignOutput.id == artifact_id).first()
            if artifact:
                key = artifact.do_key or f"DO-{artifact.id[:8]}"
                title = artifact.title or artifact.description or artifact.text or 'Design Output'
                return f"{key} – {title}"
        elif artifact_type == "vv_test":
            from models.vv_test import VVTest
            artifact = db.query(VVTest).filter(VVTest.id == artifact_id).first()
            if artifact:
                key = artifact.vv_key or f"V-{artifact.id[:8]}"
                name = artifact.name or 'V&V Test'
                return f"{key} – {name}"
    except Exception as e:
        print(f"Error getting artifact display: {e}")
        pass
    
    return f"{artifact_type} ({artifact_id[:8]})"

def build_risk_controls_doc_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    include_only_active_controls: bool = True,
    version_scope: str = "current",
    include_traceability_details: bool = True
) -> Dict[str, Any]:
    """
    Build risk control measures documentation evidence
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"id": "...", "name": "..."}]
        include_only_active_controls: If True, only include controls with status="active"
        version_scope: "current" or "all" (for risk context)
        include_traceability_details: Include trace link details
    
    Returns:
        Dictionary with risk control measures documentation data
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
    
    # Build control documentation rows
    control_rows = []
    total_controls = 0
    missing_implementation = 0
    missing_verification = 0
    
    for risk_item in risk_items:
        # Get controls for this risk item
        controls_query = db.query(RiskControl).filter(RiskControl.risk_item_id == risk_item.id)
        
        if include_only_active_controls:
            controls_query = controls_query.filter(RiskControl.status == "active")
        
        controls = controls_query.all()
        total_controls += len(controls)
        
        # Get current risk version for context
        current_version = None
        if risk_item.current_version_id:
            current_version = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        
        # Get component name
        component_name = None
        if risk_item.component_id:
            component = db.query(Component).filter(Component.id == risk_item.component_id).first()
            if component:
                component_name = component.name
        if not component_name:
            component_name = risk_item.component_name or "Unknown"
        
        for control in controls:
            # Get trace links for this control
            trace_links = []
            if include_traceability_details:
                trace_links = db.query(TraceLink).filter(
                    TraceLink.project_id == project_id,
                    TraceLink.from_type == "risk_control",
                    TraceLink.from_id == control.id
                ).all()
            
            # Partition links into implementation and verification
            implementation_refs = []
            verification_methods = []
            
            for link in trace_links:
                to_type = link.to_type
                to_id = link.to_id
                link_type = link.link_type or "traces_to"
                
                # Implementation references (design_input, design_output)
                if to_type in ["design_input", "design_output"]:
                    if link_type in ["traces_to", "impacts"]:
                        display = get_artifact_display(db, to_type, to_id)
                        implementation_refs.append({
                            "type": to_type,
                            "id": to_id,
                            "display": display,
                            "link_type": link_type,
                            "created_at": link.created_at.isoformat() if link.created_at else None
                        })
                
                # Verification methods (vv_test)
                elif to_type == "vv_test":
                    if link_type in ["verified_by", "traces_to"]:
                        display = get_artifact_display(db, to_type, to_id)
                        verification_methods.append({
                            "type": to_type,
                            "id": to_id,
                            "display": display,
                            "link_type": link_type,
                            "created_at": link.created_at.isoformat() if link.created_at else None
                        })
            
            # Check for missing evidence
            has_implementation = len(implementation_refs) > 0
            has_verification = len(verification_methods) > 0
            
            if not has_implementation:
                missing_implementation += 1
            if not has_verification:
                missing_verification += 1
            
            # Build control row
            row = {
                "risk_item_id": risk_item.id,
                "risk_key": risk_item.risk_key or f"R-{risk_item.id[:8]}",
                "component_name": component_name,
                "hazard": current_version.hazard if current_version and hasattr(current_version, 'hazard') else None,
                "harm": current_version.harm if current_version and hasattr(current_version, 'harm') else None,
                "control_id": control.id,
                "control_key": control.control_key or f"RC-{control.id[:8]}",
                "control_name": control.control_name,
                "control_type": control.control_type,
                "control_status": control.status,
                "control_description": control.control_description,
                "implementation_details": control.implementation_details,
                "verification_method": control.verification_method,
                "implementation_refs": implementation_refs,
                "verification_methods": verification_methods,
                "flags": {
                    "missing_implementation": not has_implementation,
                    "missing_verification": not has_verification
                }
            }
            
            control_rows.append(row)
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "include_only_active_controls": include_only_active_controls,
        "version_scope": version_scope,
        "rows": control_rows,
        "counts": {
            "controls": total_controls,
            "missing_implementation": missing_implementation,
            "missing_verification": missing_verification
        }
    }

