from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from models.hazard_analysis import HazardAnalysis
from schemas.hazard_analysis import HazardAnalysisCreate, HazardAnalysisUpdate

def create_hazard_analysis(db: Session, hazard_analysis: HazardAnalysisCreate) -> HazardAnalysis:
    db_hazard_analysis = HazardAnalysis(**hazard_analysis.dict())
    db.add(db_hazard_analysis)
    db.commit()
    db.refresh(db_hazard_analysis)
    return db_hazard_analysis

def get_hazard_analysis(db: Session, hazard_analysis_id: int) -> Optional[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.id == hazard_analysis_id).first()

def get_hazard_analyses_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.project_id == project_id).offset(skip).limit(limit).all()

def get_hazard_analyses_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.user_id == user_id).offset(skip).limit(limit).all()

def get_all_hazard_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).offset(skip).limit(limit).all()

def update_hazard_analysis(db: Session, hazard_analysis_id: int, hazard_analysis: HazardAnalysisUpdate) -> Optional[HazardAnalysis]:
    db_hazard_analysis = db.query(HazardAnalysis).filter(HazardAnalysis.id == hazard_analysis_id).first()
    if db_hazard_analysis:
        update_data = hazard_analysis.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_hazard_analysis, field, value)
        db.commit()
        db.refresh(db_hazard_analysis)
    return db_hazard_analysis

def delete_hazard_analysis(db: Session, hazard_analysis_id: int) -> bool:
    db_hazard_analysis = db.query(HazardAnalysis).filter(HazardAnalysis.id == hazard_analysis_id).first()
    if db_hazard_analysis:
        db.delete(db_hazard_analysis)
        db.commit()
        return True
    return False

def get_hazard_analyses_by_type(db: Session, hazard_type: str, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.hazard_type == hazard_type).offset(skip).limit(limit).all()

def get_hazard_analyses_by_risk_level(db: Session, risk_level: str, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.risk_level == risk_level).offset(skip).limit(limit).all()

def get_hazard_analyses_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(HazardAnalysis.status == status).offset(skip).limit(limit).all()

def search_hazard_analyses(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[HazardAnalysis]:
    return db.query(HazardAnalysis).filter(
        HazardAnalysis.hazard_description.contains(search_term) |
        HazardAnalysis.affected_components.contains(search_term) |
        HazardAnalysis.potential_consequences.contains(search_term)
    ).offset(skip).limit(limit).all()
