"""
Business Logic for Risk Management File (RMF) Evidence Builder
Builds comprehensive evidence package from SmartQS records
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from models.risk_control import RiskControl
from models.approval import Approval
from models.trace_link import TraceLink
from models.ai_event import AIEvent
from models.audit_log_event import AuditLogEvent
from models.component import Component
from sqlalchemy import or_

def build_rmf_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, Any]]] = None,
    include_ai_events: bool = True,
    include_audit_log: bool = True,
    include_traceability: bool = True
) -> Dict[str, Any]:
    """
    Build RMF evidence package from SmartQS records
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"id": "...", "name": "..."}]
        include_ai_events: Include AI event records
        include_audit_log: Include audit log events
        include_traceability: Include trace links
    
    Returns:
        Dictionary with all evidence data organized by risk item
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
    
    # Build evidence structure
    evidence = {
        "project_id": project_id,
        "components": component_filter or [],
        "risks": []
    }
    
    for risk_item in risk_items:
        # Get all versions (prioritize approved versions)
        versions = db.query(RiskItemVersion).filter(
            RiskItemVersion.risk_item_id == risk_item.id
        ).order_by(RiskItemVersion.version_number.desc()).all()
        
        # Get current version
        current_version = None
        if risk_item.current_version_id:
            current_version = db.query(RiskItemVersion).filter(
                RiskItemVersion.id == risk_item.current_version_id
            ).first()
        
        # Get approved versions
        approved_versions = []
        for version in versions:
            approvals = db.query(Approval).filter(
                Approval.artifact_type == "risk_item_version",
                Approval.artifact_id == version.id,
                Approval.status == "approved"
            ).all()
            if approvals:
                approved_versions.append(version.id)
        
        # Get controls
        controls = db.query(RiskControl).filter(
            RiskControl.risk_item_id == risk_item.id
        ).all()
        
        # Get approvals for all versions
        version_approvals = {}
        for version in versions:
            approvals = db.query(Approval).filter(
                Approval.artifact_type == "risk_item_version",
                Approval.artifact_id == version.id
            ).order_by(Approval.timestamp.desc()).all()
            version_approvals[version.id] = approvals
        
        # Get trace links
        links = []
        if include_traceability:
            # Links from risk item
            links_from = db.query(TraceLink).filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "risk_item",
                TraceLink.from_id == risk_item.id
            ).all()
            # Links from risk item versions
            for version in versions:
                links_from_version = db.query(TraceLink).filter(
                    TraceLink.project_id == project_id,
                    TraceLink.from_type == "risk_item_version",
                    TraceLink.from_id == version.id
                ).all()
                links_from.extend(links_from_version)
            # Links from controls
            for control in controls:
                links_from_control = db.query(TraceLink).filter(
                    TraceLink.project_id == project_id,
                    TraceLink.from_type == "risk_control",
                    TraceLink.from_id == control.id
                ).all()
                links_from.extend(links_from_control)
            
            # Links to risk item
            links_to = db.query(TraceLink).filter(
                TraceLink.project_id == project_id,
                TraceLink.to_type == "risk_item",
                TraceLink.to_id == risk_item.id
            ).all()
            
            links = list(set(links_from + links_to))  # Remove duplicates
        
        # Get AI events
        ai_events = []
        if include_ai_events:
            # Get AI events for risk item and versions
            risk_item_ai_events = db.query(AIEvent).filter(
                AIEvent.project_id == project_id,
                AIEvent.context_type == "risk_item",
                AIEvent.context_id == risk_item.id
            ).order_by(AIEvent.created_at.desc()).all()
            ai_events.extend(risk_item_ai_events)
            
            for version in versions:
                version_ai_events = db.query(AIEvent).filter(
                    AIEvent.project_id == project_id,
                    AIEvent.context_type == "risk_item_version",
                    AIEvent.context_id == version.id
                ).order_by(AIEvent.created_at.desc()).all()
                ai_events.extend(version_ai_events)
        
        # Get audit log events (filter by event_type patterns)
        audit_events = []
        if include_audit_log:
            # Get audit events related to risk items (handoff events)
            risk_item_audit_events = db.query(AuditLogEvent).filter(
                AuditLogEvent.project_id == project_id,
                AuditLogEvent.event_type.like("handoff.risk.%")
            ).order_by(AuditLogEvent.created_at.desc()).all()
            # Filter by details_json containing risk_item_id
            filtered_events = []
            for event in risk_item_audit_events:
                if event.details_json and isinstance(event.details_json, dict):
                    if event.details_json.get("risk_item_id") == risk_item.id:
                        filtered_events.append(event)
            audit_events.extend(filtered_events)
        
        # Build risk evidence structure
        risk_evidence = {
            "risk_item": {
                "id": risk_item.id,
                "risk_key": risk_item.risk_key,
                "title": risk_item.title,
                "description": risk_item.description,
                "category": risk_item.category,
                "status": risk_item.status,
                "component_id": risk_item.component_id,
                "component_name": risk_item.component_name
            },
            "current_version": {
                "id": current_version.id if current_version else None,
                "version_number": current_version.version_number if current_version else None,
                "hazard": current_version.hazard if current_version else None,
                "hazardous_situation": current_version.hazardous_situation if current_version else None,
                "harm": current_version.harm if current_version else None,
                "sequence_of_events": current_version.sequence_of_events if current_version else None,
                "failure_mode": current_version.failure_mode if current_version else None,
                "severity": current_version.severity if current_version else None,
                "probability_of_harm": current_version.probability_of_harm if current_version else None,
                "risk_score": current_version.risk_score if current_version else None,
                "risk_acceptability": current_version.risk_acceptability if current_version else None,
                "risk_rationale": current_version.risk_rationale if current_version else None,
                "residual_severity": current_version.residual_severity if current_version else None,
                "residual_probability_of_harm": current_version.residual_probability_of_harm if current_version else None,
                "residual_risk_score": current_version.residual_risk_score if current_version else None,
                "benefit_risk_summary": current_version.benefit_risk_summary if current_version else None,
                "overall_residual_risk_conclusion": current_version.overall_residual_risk_conclusion if current_version else None,
            } if current_version else None,
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "hazard": v.hazard,
                    "hazardous_situation": v.hazardous_situation,
                    "harm": v.harm,
                    "sequence_of_events": v.sequence_of_events,
                    "failure_mode": v.failure_mode,
                    "severity": v.severity,
                    "probability_of_harm": v.probability_of_harm,
                    "risk_score": v.risk_score,
                    "risk_acceptability": v.risk_acceptability,
                    "risk_rationale": v.risk_rationale,
                    "residual_severity": v.residual_severity,
                    "residual_probability_of_harm": v.residual_probability_of_harm,
                    "residual_risk_score": v.residual_risk_score,
                    "benefit_risk_summary": v.benefit_risk_summary,
                    "overall_residual_risk_conclusion": v.overall_residual_risk_conclusion,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                    "is_approved": v.id in approved_versions,
                    "is_current": v.id == (current_version.id if current_version else None)
                }
                for v in versions
            ],
            "controls": [
                {
                    "id": c.id,
                    "control_key": c.control_key,
                    "control_name": c.control_name,
                    "control_description": c.control_description,
                    "control_type": c.control_type,
                    "status": c.status,
                    "implementation_details": c.implementation_details,
                    "verification_method": c.verification_method
                }
                for c in controls
            ],
            "approvals": [
                {
                    "version_id": version_id,
                    "approvals": [
                        {
                            "id": a.id,
                            "approver_id": a.approver_id,
                            "status": a.status,
                            "comment": a.comment,
                            "timestamp": a.timestamp.isoformat() if a.timestamp else None
                        }
                        for a in approvals
                    ]
                }
                for version_id, approvals in version_approvals.items()
            ],
            "links": [
                {
                    "id": l.id,
                    "from_type": l.from_type,
                    "from_id": l.from_id,
                    "to_type": l.to_type,
                    "to_id": l.to_id,
                    "link_type": l.link_type,
                    "rationale": l.rationale
                }
                for l in links
            ],
            "ai_events": [
                {
                    "id": e.id,
                    "context_type": e.context_type,
                    "context_id": e.context_id,
                    "prompt_name": e.prompt_name,
                    "disposition": e.disposition,
                    "disposition_notes": e.disposition_notes,
                    "input_summary": e.input_summary,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in ai_events
            ],
            "audit_events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "details_json": e.details_json,
                    "created_at": e.created_at.isoformat() if e.created_at else None
                }
                for e in audit_events
            ]
        }
        
        evidence["risks"].append(risk_evidence)
    
    return evidence

