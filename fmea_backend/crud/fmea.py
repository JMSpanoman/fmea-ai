from sqlalchemy.orm import Session
from models.fmea import FMEARow
from models.fmea_version import FMEAVersion
from schemas.fmea import FMEARowCreate, FMEARowUpdate
from typing import List, Optional, Dict, Any
import uuid
import json

def _calculate_rpn(severity: Optional[int], probability: Optional[int], detection: Optional[int]) -> Optional[int]:
    """Calculate RPN from severity, probability, and detection"""
    if severity is not None and probability is not None and detection is not None:
        return severity * probability * detection
    return None

def _calculate_diff(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate diff between old and new FMEA row data"""
    diff = {}
    for key in set(old_data.keys()) | set(new_data.keys()):
        old_val = old_data.get(key)
        new_val = new_data.get(key)
        if old_val != new_val:
            diff[key] = {"old": old_val, "new": new_val}
    return diff

def _serialize_for_diff(row: FMEARow) -> Dict[str, Any]:
    """Serialize FMEA row for diff calculation"""
    return {
        "failure_mode": row.failure_mode,
        "effect": row.effect,
        "cause": row.cause,
        "severity": row.severity,
        "probability": row.probability,
        "detection": row.detection,
        "rpn": row.rpn,
        "mitigation": row.mitigation,
        "residual_severity": row.residual_severity,
        "residual_probability": row.residual_probability,
        "residual_detection": row.residual_detection,
        "residual_rpn": row.residual_rpn,
        "financial_impact": float(row.financial_impact) if row.financial_impact else None,
        "component_id": row.component_id,
        "hazard_library_id": getattr(row, "hazard_library_id", None),
        "harm_library_id": getattr(row, "harm_library_id", None),
        "risk_control_library_id": getattr(row, "risk_control_library_id", None),
        "verification_library_id": getattr(row, "verification_library_id", None),
    }

def create_fmea_row(db: Session, fmea_row: FMEARowCreate) -> FMEARow:
    """Create a new FMEA row with auto-calculated RPN"""
    db_row = FMEARow(
        id=str(uuid.uuid4()),
        project_id=fmea_row.project_id,
        component_id=fmea_row.component_id,
        failure_mode=fmea_row.failure_mode,
        effect=fmea_row.effect,
        cause=fmea_row.cause,
        severity=fmea_row.severity,
        probability=fmea_row.probability,
        detection=fmea_row.detection,
        mitigation=fmea_row.mitigation,
        residual_severity=fmea_row.residual_severity,
        residual_probability=fmea_row.residual_probability,
        residual_detection=fmea_row.residual_detection,
        financial_impact=fmea_row.financial_impact,
        ai_metadata=fmea_row.ai_metadata,
        hazard_library_id=getattr(fmea_row, "hazard_library_id", None),
        harm_library_id=getattr(fmea_row, "harm_library_id", None),
        risk_control_library_id=getattr(fmea_row, "risk_control_library_id", None),
        verification_library_id=getattr(fmea_row, "verification_library_id", None),
        version=1
    )
    
    # Auto-calculate RPN
    db_row.rpn = _calculate_rpn(db_row.severity, db_row.probability, db_row.detection)
    db_row.residual_rpn = _calculate_rpn(
        db_row.residual_severity, 
        db_row.residual_probability, 
        db_row.residual_detection
    )
    
    db.add(db_row)
    db.commit()
    db.refresh(db_row)
    return db_row

def get_fmea_rows_by_project(db: Session, project_id: str) -> List[FMEARow]:
    """Get all FMEA rows for a project"""
    return db.query(FMEARow).filter(FMEARow.project_id == project_id).all()

def get_fmea_row(db: Session, fmea_row_id: str, project_id: str) -> Optional[FMEARow]:
    """Get a specific FMEA row by ID"""
    return db.query(FMEARow).filter(
        FMEARow.id == fmea_row_id,
        FMEARow.project_id == project_id
    ).first()

def update_fmea_row(db: Session, fmea_row_id: str, fmea_row: FMEARowUpdate, project_id: str) -> Optional[FMEARow]:
    """Update an FMEA row with versioning"""
    db_row = get_fmea_row(db, fmea_row_id, project_id)
    if not db_row:
        return None
    
    # Store old data for diff
    old_data = _serialize_for_diff(db_row)
    
    # Update fields
    # Pydantic v2 compatibility
    if hasattr(fmea_row, 'model_dump'):
        update_data = fmea_row.model_dump(exclude_unset=True)
    else:
        update_data = fmea_row.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_row, field, value)
    
    # Auto-calculate RPN
    db_row.rpn = _calculate_rpn(db_row.severity, db_row.probability, db_row.detection)
    db_row.residual_rpn = _calculate_rpn(
        db_row.residual_severity,
        db_row.residual_probability,
        db_row.residual_detection
    )
    
    # Create version entry with diff
    new_data = _serialize_for_diff(db_row)
    diff = _calculate_diff(old_data, new_data)
    
    if diff:  # Only create version if there are changes
        db_row.version += 1
        version_entry = FMEAVersion(
            id=str(uuid.uuid4()),
            fmea_row_id=db_row.id,
            version=db_row.version,
            diff=diff
        )
        db.add(version_entry)
    
    db.commit()
    db.refresh(db_row)
    return db_row

def delete_fmea_row(db: Session, fmea_row_id: str, project_id: str) -> bool:
    """Delete an FMEA row"""
    db_row = get_fmea_row(db, fmea_row_id, project_id)
    if not db_row:
        return False
    
    db.delete(db_row)
    db.commit()
    return True

def get_fmea_version_history(db: Session, fmea_row_id: str, project_id: str) -> List[FMEAVersion]:
    """Get version history for an FMEA row"""
    # Verify the row belongs to the project
    row = get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        return []
    
    return db.query(FMEAVersion).filter(
        FMEAVersion.fmea_row_id == fmea_row_id
    ).order_by(FMEAVersion.version.desc()).all()
