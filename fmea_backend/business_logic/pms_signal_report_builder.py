"""
Business Logic for PMS Signal Feedback Report Evidence Builder
Builds PMS signal feedback evidence from SmartQS pms_signals and trace_links
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.pms_signal import PMSSignal
from models.trace_link import TraceLink
from models.risk_item import RiskItem
from models.capa import CAPA
from models.change_control import ChangeControl
from datetime import datetime
import json

def get_artifact_display(db: Session, artifact_type: str, artifact_id: str) -> str:
    """Get display label for an artifact"""
    try:
        if artifact_type == "risk_item":
            artifact = db.query(RiskItem).filter(RiskItem.id == artifact_id).first()
            if artifact:
                return f"{artifact.risk_key or f'R-{artifact.id[:8]}'} – {artifact.title or 'Risk Item'}"
        elif artifact_type == "capa":
            artifact = db.query(CAPA).filter(CAPA.id == artifact_id).first()
            if artifact:
                return f"{artifact.capa_key or f'CAPA-{artifact.id[:8]}'} – {artifact.title or 'CAPA'}"
        elif artifact_type == "change_control":
            artifact = db.query(ChangeControl).filter(ChangeControl.id == artifact_id).first()
            if artifact:
                return f"{artifact.change_key or f'CHG-{artifact.id[:8]}'} – {artifact.title or 'Change Control'}"
    except Exception as e:
        print(f"Error getting artifact display: {e}")
        pass
    
    return f"{artifact_type} ({artifact_id[:8]})"

def build_pms_signal_feedback_evidence(
    db: Session,
    project_id: str,
    component_filter: Optional[List[Dict[str, str]]] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    include_open_only: bool = False,
    include_traceability: bool = True,
    include_actions: bool = True
) -> Dict[str, Any]:
    """
    Build PMS signal feedback evidence
    
    Args:
        db: Database session
        project_id: Project ID
        component_filter: List of component filters [{"name": "..."}]
        date_from: Start date filter
        date_to: End date filter
        include_open_only: If True, only include open signals
        include_traceability: Include trace links
        include_actions: Include CAPA/Change actions
    
    Returns:
        Dictionary with PMS signal feedback evidence
    """
    # Extract component names from filter
    component_names = []
    if component_filter:
        for comp in component_filter:
            if comp.get("name"):
                component_names.append(comp["name"])
    
    # Query signals
    query = db.query(PMSSignal).filter(PMSSignal.project_id == project_id)
    
    # Filter by components
    if component_names:
        for component_name in component_names:
            query = query.filter(PMSSignal.component_names_json.contains([component_name]))
    
    # Filter by date range
    if date_from:
        query = query.filter(PMSSignal.date_detected >= date_from)
    if date_to:
        query = query.filter(PMSSignal.date_detected <= date_to)
    
    # Filter by status
    if include_open_only:
        query = query.filter(PMSSignal.status == "open")
    
    signals = query.order_by(PMSSignal.date_detected.desc()).all()
    
    # Build signal evidence with links
    signal_evidence = []
    total_signals = len(signals)
    signals_under_review = 0
    signals_confirmed = 0
    signals_triggered_risk = 0
    signals_resulted_capa = 0
    signals_resulted_change = 0
    signals_no_risk_link = 0
    
    for signal in signals:
        # Get trace links
        links = {
            "risk_items": [],
            "capas": [],
            "change_controls": []
        }
        
        if include_traceability:
            trace_links = db.query(TraceLink).filter(
                TraceLink.project_id == project_id,
                TraceLink.from_type == "pms_signal",
                TraceLink.from_id == signal.id
            ).all()
            
            for link in trace_links:
                to_type = link.to_type
                to_id = link.to_id
                
                if to_type == "risk_item":
                    display = get_artifact_display(db, "risk_item", to_id)
                    links["risk_items"].append({
                        "id": to_id,
                        "display": display,
                        "link_type": link.link_type or "impacts",
                        "created_at": link.created_at.isoformat() if link.created_at else None
                    })
                elif to_type == "capa":
                    display = get_artifact_display(db, "capa", to_id)
                    links["capas"].append({
                        "id": to_id,
                        "display": display,
                        "link_type": link.link_type or "generated_from",
                        "created_at": link.created_at.isoformat() if link.created_at else None
                    })
                elif to_type == "change_control":
                    display = get_artifact_display(db, "change_control", to_id)
                    links["change_controls"].append({
                        "id": to_id,
                        "display": display,
                        "link_type": link.link_type or "generated_from",
                        "created_at": link.created_at.isoformat() if link.created_at else None
                    })
        
        # Count statistics
        if signal.trend_status == "under_review":
            signals_under_review += 1
        elif signal.trend_status == "confirmed":
            signals_confirmed += 1
        
        if signal.trigger_status != "not_triggered":
            signals_triggered_risk += 1
        
        if len(links["capas"]) > 0:
            signals_resulted_capa += 1
        
        if len(links["change_controls"]) > 0:
            signals_resulted_change += 1
        
        if len(links["risk_items"]) == 0:
            signals_no_risk_link += 1
        
        signal_data = {
            "signal": {
                "id": signal.id,
                "signal_key": signal.signal_key,
                "signal_type": signal.signal_type,
                "component_names": signal.component_names_json,
                "title": signal.title,
                "description": signal.description,
                "source_ref": signal.source_ref,
                "date_detected": signal.date_detected.isoformat() if signal.date_detected else None,
                "severity_observed": signal.severity_observed,
                "frequency_observed": signal.frequency_observed,
                "rate_observed": float(signal.rate_observed) if signal.rate_observed else None,
                "trend_status": signal.trend_status,
                "trigger_status": signal.trigger_status,
                "recommended_action": signal.recommended_action,
                "owner": signal.owner,
                "status": signal.status
            },
            "links": links if include_traceability else {"risk_items": [], "capas": [], "change_controls": []}
        }
        
        signal_evidence.append(signal_data)
    
    # Build gaps list
    gaps = {
        "signals_missing_risk_link": [
            {
                "signal_key": s["signal"]["signal_key"],
                "signal_id": s["signal"]["id"],
                "title": s["signal"]["title"]
            }
            for s in signal_evidence if len(s["links"]["risk_items"]) == 0
        ],
        "signals_missing_action_despite_trigger": [
            {
                "signal_key": s["signal"]["signal_key"],
                "signal_id": s["signal"]["id"],
                "title": s["signal"]["title"],
                "trigger_status": s["signal"]["trigger_status"]
            }
            for s in signal_evidence
            if s["signal"]["trigger_status"] != "not_triggered"
            and len(s["links"]["capas"]) == 0
            and len(s["links"]["change_controls"]) == 0
        ]
    }
    
    return {
        "project_id": project_id,
        "components": component_filter or [],
        "date_from": date_from.isoformat() if date_from else None,
        "date_to": date_to.isoformat() if date_to else None,
        "signals": signal_evidence,
        "summary": {
            "total_signals": total_signals,
            "signals_under_review": signals_under_review,
            "signals_confirmed": signals_confirmed,
            "signals_triggered_risk": signals_triggered_risk,
            "signals_resulted_capa": signals_resulted_capa,
            "signals_resulted_change": signals_resulted_change,
            "signals_no_risk_link": signals_no_risk_link
        },
        "gaps": gaps
    }

