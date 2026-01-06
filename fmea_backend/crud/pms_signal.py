from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from models.pms_signal import PMSSignal
from schemas.pms_signal import PMSSignalCreate, PMSSignalUpdate
from datetime import datetime
import json

def create_pms_signal(db: Session, signal: PMSSignalCreate, project_id: str, created_by: str) -> PMSSignal:
    """Create a new PMS signal"""
    db_signal = PMSSignal(
        project_id=project_id,
        signal_key=signal.signal_key,
        signal_type=signal.signal_type,
        component_names_json=signal.component_names_json,
        title=signal.title,
        description=signal.description,
        source_ref=signal.source_ref,
        date_detected=signal.date_detected,
        severity_observed=signal.severity_observed,
        frequency_observed=signal.frequency_observed,
        rate_observed=signal.rate_observed,
        trend_status=signal.trend_status,
        trigger_status=signal.trigger_status,
        recommended_action=signal.recommended_action,
        owner=signal.owner,
        status=signal.status,
        created_by=created_by
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal

def get_pms_signal(db: Session, signal_id: str, project_id: str) -> Optional[PMSSignal]:
    """Get a PMS signal by ID"""
    return db.query(PMSSignal).filter(
        PMSSignal.id == signal_id,
        PMSSignal.project_id == project_id
    ).first()

def get_pms_signals(
    db: Session,
    project_id: str,
    component_filter: Optional[List[str]] = None,
    signal_type: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[PMSSignal]:
    """Get PMS signals with filters"""
    query = db.query(PMSSignal).filter(PMSSignal.project_id == project_id)
    
    if component_filter:
        # Filter by component names in JSON
        for component in component_filter:
            query = query.filter(PMSSignal.component_names_json.contains([component]))
    
    if signal_type:
        query = query.filter(PMSSignal.signal_type == signal_type)
    
    if status:
        query = query.filter(PMSSignal.status == status)
    
    if date_from:
        query = query.filter(PMSSignal.date_detected >= date_from)
    
    if date_to:
        query = query.filter(PMSSignal.date_detected <= date_to)
    
    return query.order_by(PMSSignal.date_detected.desc()).offset(skip).limit(limit).all()

def update_pms_signal(
    db: Session,
    signal_id: str,
    project_id: str,
    signal_update: PMSSignalUpdate
) -> Optional[PMSSignal]:
    """Update a PMS signal"""
    signal = get_pms_signal(db, signal_id, project_id)
    if not signal:
        return None
    
    update_data = signal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(signal, field, value)
    
    db.commit()
    db.refresh(signal)
    return signal

def delete_pms_signal(db: Session, signal_id: str, project_id: str) -> bool:
    """Delete a PMS signal"""
    signal = get_pms_signal(db, signal_id, project_id)
    if not signal:
        return False
    
    db.delete(signal)
    db.commit()
    return True

