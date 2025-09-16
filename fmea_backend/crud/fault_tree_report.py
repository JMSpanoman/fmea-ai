from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from models.fault_tree_report import FaultTreeReport
from schemas.fault_tree_report import FaultTreeReportCreate, FaultTreeReportUpdate

def create_fault_tree_report(db: Session, fault_tree_report: FaultTreeReportCreate) -> FaultTreeReport:
    db_fault_tree_report = FaultTreeReport(**fault_tree_report.dict())
    db.add(db_fault_tree_report)
    db.commit()
    db.refresh(db_fault_tree_report)
    return db_fault_tree_report

def get_fault_tree_report(db: Session, fault_tree_report_id: int) -> Optional[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.id == fault_tree_report_id).first()

def get_fault_tree_reports_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.project_id == project_id).offset(skip).limit(limit).all()

def get_fault_tree_reports_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.user_id == user_id).offset(skip).limit(limit).all()

def get_all_fault_tree_reports(db: Session, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).offset(skip).limit(limit).all()

def update_fault_tree_report(db: Session, fault_tree_report_id: int, fault_tree_report: FaultTreeReportUpdate) -> Optional[FaultTreeReport]:
    db_fault_tree_report = db.query(FaultTreeReport).filter(FaultTreeReport.id == fault_tree_report_id).first()
    if db_fault_tree_report:
        update_data = fault_tree_report.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_fault_tree_report, field, value)
        db.commit()
        db.refresh(db_fault_tree_report)
    return db_fault_tree_report

def delete_fault_tree_report(db: Session, fault_tree_report_id: int) -> bool:
    db_fault_tree_report = db.query(FaultTreeReport).filter(FaultTreeReport.id == fault_tree_report_id).first()
    if db_fault_tree_report:
        db.delete(db_fault_tree_report)
        db.commit()
        return True
    return False

def get_fault_tree_reports_by_type(db: Session, fault_tree_type: str, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.fault_tree_type == fault_tree_type).offset(skip).limit(limit).all()

def get_fault_tree_reports_by_risk_level(db: Session, risk_level: str, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.risk_level == risk_level).offset(skip).limit(limit).all()

def get_fault_tree_reports_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(FaultTreeReport.status == status).offset(skip).limit(limit).all()

def search_fault_tree_reports(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[FaultTreeReport]:
    return db.query(FaultTreeReport).filter(
        FaultTreeReport.top_event.contains(search_term) |
        FaultTreeReport.root_causes.contains(search_term) |
        FaultTreeReport.basic_events.contains(search_term)
    ).offset(skip).limit(limit).all()
