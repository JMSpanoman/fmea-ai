from sqlalchemy.orm import Session
from models.capa import CAPA
from schemas.capa import CAPACreate, CAPAUpdate
from typing import List, Optional
import uuid

def create_capa(db: Session, capa: CAPACreate) -> CAPA:
    """Create a new CAPA"""
    db_capa = CAPA(
        id=str(uuid.uuid4()),
        project_id=capa.project_id,
        root_cause=capa.root_cause,
        capa_plan=capa.capa_plan,
        effectiveness_check=capa.effectiveness_check,
        linked_risk_ids=capa.linked_risk_ids or [],
        ai_metadata=capa.ai_metadata
    )
    db.add(db_capa)
    db.commit()
    db.refresh(db_capa)
    return db_capa

def get_capas_by_project(db: Session, project_id: str) -> List[CAPA]:
    """Get all CAPAs for a project"""
    return db.query(CAPA).filter(CAPA.project_id == project_id).all()

def get_capa(db: Session, capa_id: str, project_id: str) -> Optional[CAPA]:
    """Get a specific CAPA"""
    return db.query(CAPA).filter(
        CAPA.id == capa_id,
        CAPA.project_id == project_id
    ).first()

def update_capa(db: Session, capa_id: str, capa: CAPAUpdate, project_id: str) -> Optional[CAPA]:
    """Update a CAPA"""
    db_capa = get_capa(db, capa_id, project_id)
    if not db_capa:
        return None
    
    update_data = capa.model_dump(exclude_unset=True) if hasattr(capa, 'model_dump') else capa.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_capa, field, value)
    
    db.commit()
    db.refresh(db_capa)
    return db_capa

def delete_capa(db: Session, capa_id: str, project_id: str) -> bool:
    """Delete a CAPA"""
    db_capa = get_capa(db, capa_id, project_id)
    if not db_capa:
        return False
    
    db.delete(db_capa)
    db.commit()
    return True
