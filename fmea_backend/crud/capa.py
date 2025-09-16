from sqlalchemy.orm import Session
from models.capa import CAPA
from schemas.capa import CAPACreate, CAPAUpdate
from typing import List, Optional

def create_capa(db: Session, project_id: int, capa_data: CAPACreate, user_id: str) -> CAPA:
    """Create a new CAPA entry"""
    db_capa = CAPA(
        project_id=project_id,
        user_id=user_id,
        issue_description=capa_data.issue_description,
        source=capa_data.source,
        detection_date=capa_data.detection_date,
        severity=capa_data.severity,
        root_cause=capa_data.root_cause,
        corrective_action=capa_data.corrective_action,
        preventive_action=capa_data.preventive_action,
        action_owner=capa_data.action_owner,
        due_date=capa_data.due_date,
        status=capa_data.status,
        effectiveness_check_plan=capa_data.effectiveness_check_plan,
        fmea_link=capa_data.fmea_link,
        regulatory_impact=capa_data.regulatory_impact,
        closure_summary=capa_data.closure_summary,
        milestones=capa_data.milestones,
        risk_controls_update=capa_data.risk_controls_update,
        analysis_timestamp=capa_data.analysis_timestamp,
        version=capa_data.version
    )
    db.add(db_capa)
    db.commit()
    db.refresh(db_capa)
    return db_capa

def get_capas_for_project(db: Session, project_id: int, user_id: str) -> List[CAPA]:
    """Get all CAPA entries for a project"""
    return db.query(CAPA).filter(CAPA.project_id == project_id, CAPA.user_id == user_id).all()

def get_capa(db: Session, capa_id: int, user_id: str) -> Optional[CAPA]:
    """Get a specific CAPA entry"""
    return db.query(CAPA).filter(CAPA.id == capa_id, CAPA.user_id == user_id).first()

def update_capa(db: Session, capa_id: int, capa_data: CAPAUpdate, user_id: str) -> Optional[CAPA]:
    """Update a CAPA entry"""
    db_capa = db.query(CAPA).filter(CAPA.id == capa_id, CAPA.user_id == user_id).first()
    if db_capa:
        for field, value in capa_data.dict(exclude_unset=True).items():
            setattr(db_capa, field, value)
        db.commit()
        db.refresh(db_capa)
    return db_capa

def delete_capa(db: Session, capa_id: int, user_id: str) -> bool:
    """Delete a CAPA entry"""
    db_capa = db.query(CAPA).filter(CAPA.id == capa_id, CAPA.user_id == user_id).first()
    if db_capa:
        db.delete(db_capa)
        db.commit()
        return True
    return False 