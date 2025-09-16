from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import os
from models.fmea import FMEA
from schemas import fmea as fmea_schemas
from datetime import datetime
import json

def create_fmea(db: Session, project_id: int, fmea: fmea_schemas.FMEACreate, user_id: str) -> FMEA:
    """Create a new FMEA entry"""
    db_fmea = FMEA(
        project_id=project_id,
        user_id=user_id,
        component=fmea.component,
        failure_mode=fmea.failure_mode,
        effect=fmea.effect,
        cause=fmea.cause,
        severity=fmea.severity,
        occurrence=fmea.occurrence,
        detection=fmea.detection,
        rpn=fmea.rpn,
        mitigation=fmea.mitigation,
        action_taken=fmea.action_taken,
        revised_severity=fmea.revised_severity,
        revised_occurrence=fmea.revised_occurrence,
        revised_detection=fmea.revised_detection,
        revised_rpn=fmea.revised_rpn
    )
    db.add(db_fmea)
    db.commit()
    db.refresh(db_fmea)
    return db_fmea

def get_fmeas_for_project(db: Session, project_id: int, user_id: str) -> List[FMEA]:
    """Get all FMEA entries for a project"""
    return db.query(FMEA).filter(
        and_(
            FMEA.project_id == project_id,
            FMEA.user_id == user_id
        )
    ).all()

def get_fmea(db: Session, project_id: int, fmea_id: int, user_id: str) -> Optional[FMEA]:
    """Get a specific FMEA entry"""
    return db.query(FMEA).filter(
        and_(
            FMEA.id == fmea_id,
            FMEA.project_id == project_id,
            FMEA.user_id == user_id
        )
    ).first()

def update_fmea(db: Session, project_id: int, fmea_id: int, fmea: fmea_schemas.FMEAUpdate, user_id: str) -> Optional[FMEA]:
    """Update a FMEA entry"""
    db_fmea = get_fmea(db, project_id, fmea_id, user_id)
    if not db_fmea:
        return None
    
    update_data = fmea.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fmea, field, value)
    
    db_fmea.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_fmea)
    return db_fmea

def delete_fmea(db: Session, project_id: int, fmea_id: int, user_id: str) -> bool:
    """Delete a FMEA entry"""
    db_fmea = get_fmea(db, project_id, fmea_id, user_id)
    if not db_fmea:
        return False
    
    db.delete(db_fmea)
    db.commit()
    return True

def get_ai_suggestions(request: fmea_schemas.AISuggestionRequest, user_id: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    # If no API key is set, return mock data for demonstration
    if not api_key or api_key == "your-openai-api-key-here":
        mock_suggestions = [
            {
                "failure_mode": "False reading",
                "effect": "Incorrect measurement",
                "cause": "Sensor drift",
                "severity": 7,
                "occurrence": 4,
                "detection": 6,
                "rpn": 168,
                "mitigation": "Regular calibration",
                "action_taken": "Implement calibration schedule"
            },
            {
                "failure_mode": "No output",
                "effect": "System failure",
                "cause": "Power supply failure",
                "severity": 9,
                "occurrence": 3,
                "detection": 5,
                "rpn": 135,
                "mitigation": "Redundant power supply",
                "action_taken": "Install backup power"
            }
        ]
        return {
            "suggestions": mock_suggestions,
            "message": "Mock suggestions (OpenAI API key not configured)"
        }
    
    # TODO: Implement actual OpenAI API call
    return {
        "suggestions": [],
        "message": "OpenAI integration not yet implemented"
    }

def export_fmea_csv(db: Session, project_id: int, user_id: str) -> dict:
    """Export FMEA data as CSV"""
    fmeas = get_fmeas_for_project(db, project_id, user_id)
    
    csv_data = []
    for fmea in fmeas:
        csv_data.append({
            "Component": fmea.component,
            "Failure Mode": fmea.failure_mode,
            "Effect": fmea.effect,
            "Cause": fmea.cause,
            "Severity": fmea.severity,
            "Occurrence": fmea.occurrence,
            "Detection": fmea.detection,
            "RPN": fmea.rpn,
            "Mitigation": fmea.mitigation,
            "Action Taken": fmea.action_taken,
            "Revised Severity": fmea.revised_severity,
            "Revised Occurrence": fmea.revised_occurrence,
            "Revised Detection": fmea.revised_detection,
            "Revised RPN": fmea.revised_rpn
        })
    
    return {"data": csv_data}

def export_fmea_pdf(db: Session, project_id: int, user_id: str) -> dict:
    """Export FMEA data as PDF"""
    # TODO: Implement PDF generation
    return {"message": "PDF export not yet implemented"}