from sqlalchemy.orm import Session
from models.trace_link import TraceLink
from models.risk_item import RiskItem
from models.risk_control import RiskControl
from models.risk_item_version import RiskItemVersion
from models.design_input import DesignInput
from models.design_output import DesignOutput
from models.vv_test import VVTest
from models.capa import CAPA
from models.change_control import ChangeControl
from models.fmea import FMEARow
from schemas.trace import TraceLinkCreate
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import uuid

# Canonical type validation
CANONICAL_FROM_TYPES = {
    "risk_item", "risk_item_version", "risk_control",
    "design_input", "design_output", "vv_test",
    "capa", "change_control", "fmea_row", "pms_signal"
}

CANONICAL_TO_TYPES = CANONICAL_FROM_TYPES  # Same set

CANONICAL_LINK_TYPES = {
    "traces_to", "verified_by", "generated_from",
    "impacts", "mitigates", "links_to"
}

def validate_trace_link_types(from_type: str, to_type: str, link_type: Optional[str] = None) -> None:
    """Validate that trace link types are canonical"""
    if from_type not in CANONICAL_FROM_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid from_type: {from_type}. Must be one of: {sorted(CANONICAL_FROM_TYPES)}"
        )
    if to_type not in CANONICAL_TO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid to_type: {to_type}. Must be one of: {sorted(CANONICAL_TO_TYPES)}"
        )
    if link_type and link_type not in CANONICAL_LINK_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid link_type: {link_type}. Must be one of: {sorted(CANONICAL_LINK_TYPES)}"
        )

def validate_target_artifact_exists(db: Session, artifact_type: str, artifact_id: str, project_id: str) -> bool:
    """Validate that the target artifact exists (referential integrity check)"""
    type_to_model = {
        "risk_item": RiskItem,
        "risk_item_version": RiskItemVersion,
        "risk_control": RiskControl,
        "design_input": DesignInput,
        "design_output": DesignOutput,
        "vv_test": VVTest,
        "capa": CAPA,
        "change_control": ChangeControl,
        "fmea_row": FMEARow,
        # Note: pms_signal validation can be added when PMSSignal model is available
    }
    
    model_class = type_to_model.get(artifact_type)
    if not model_class:
        # For unknown types, skip validation (allows future extensibility)
        return True
    
    artifact = db.query(model_class).filter(
        model_class.id == artifact_id,
        model_class.project_id == project_id
    ).first()
    
    return artifact is not None

def create_trace_link(db: Session, trace_link: TraceLinkCreate) -> TraceLink:
    """Create a new trace link with validation and referential integrity checks"""
    # Validate canonical types
    validate_trace_link_types(
        trace_link.from_type,
        trace_link.to_type,
        getattr(trace_link, 'link_type', None)
    )
    
    # Validate referential integrity: target artifact must exist
    if not validate_target_artifact_exists(db, trace_link.to_type, trace_link.to_id, trace_link.project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target artifact not found: {trace_link.to_type} with id {trace_link.to_id} does not exist in this project"
        )
    
    # Also validate source artifact exists (for consistency)
    if not validate_target_artifact_exists(db, trace_link.from_type, trace_link.from_id, trace_link.project_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source artifact not found: {trace_link.from_type} with id {trace_link.from_id} does not exist in this project"
        )
    
    # Check if reverse link already exists to avoid duplicates
    existing = db.query(TraceLink).filter(
        TraceLink.project_id == trace_link.project_id,
        TraceLink.from_type == trace_link.to_type,
        TraceLink.from_id == trace_link.to_id,
        TraceLink.to_type == trace_link.from_type,
        TraceLink.to_id == trace_link.from_id
    ).first()
    
    if existing:
        return existing
    
    db_link = TraceLink(
        id=str(uuid.uuid4()),
        project_id=trace_link.project_id,
        from_type=trace_link.from_type,
        from_id=trace_link.from_id,
        to_type=trace_link.to_type,
        to_id=trace_link.to_id,
        link_type=getattr(trace_link, 'link_type', 'traces_to')
    )
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

def get_trace_links_by_project(db: Session, project_id: str) -> List[TraceLink]:
    """Get all trace links for a project"""
    return db.query(TraceLink).filter(TraceLink.project_id == project_id).all()

def get_trace_links_from(db: Session, from_type: str, from_id: str, project_id: str) -> List[TraceLink]:
    """Get all trace links from a specific artifact"""
    return db.query(TraceLink).filter(
        TraceLink.project_id == project_id,
        TraceLink.from_type == from_type,
        TraceLink.from_id == from_id
    ).all()

def get_trace_links_to(db: Session, to_type: str, to_id: str, project_id: str) -> List[TraceLink]:
    """Get all trace links to a specific artifact"""
    return db.query(TraceLink).filter(
        TraceLink.project_id == project_id,
        TraceLink.to_type == to_type,
        TraceLink.to_id == to_id
    ).all()

def get_trace_matrix(db: Session, project_id: str) -> Dict[str, Any]:
    """Get traceability matrix as a graph structure"""
    links = get_trace_links_by_project(db, project_id)
    
    # Build bidirectional graph representation
    graph: Dict[str, Dict[str, List[str]]] = {}
    
    for link in links:
        from_key = f"{link.from_type}:{link.from_id}"
        to_key = f"{link.to_type}:{link.to_id}"
        
        # Add forward link
        if from_key not in graph:
            graph[from_key] = {"outgoing": [], "incoming": []}
        if to_key not in graph:
            graph[to_key] = {"outgoing": [], "incoming": []}
        
        graph[from_key]["outgoing"].append(to_key)
        graph[to_key]["incoming"].append(from_key)
    
    return {
        "links": links,
        "graph": graph
    }

def delete_trace_link(db: Session, link_id: str, project_id: str) -> bool:
    """Delete a trace link"""
    db_link = db.query(TraceLink).filter(
        TraceLink.id == link_id,
        TraceLink.project_id == project_id
    ).first()
    
    if not db_link:
        return False
    
    db.delete(db_link)
    db.commit()
    return True

def create_trace_link_bidirectional(db: Session, project_id: str, from_type: str, from_id: str, to_type: str, to_id: str) -> TraceLink:
    """Create a trace link (handles bidirectional representation)"""
    trace_link = TraceLinkCreate(
        project_id=project_id,
        from_type=from_type,
        from_id=from_id,
        to_type=to_type,
        to_id=to_id
    )
    return create_trace_link(db, trace_link)

