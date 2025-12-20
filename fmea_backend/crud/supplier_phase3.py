from sqlalchemy.orm import Session
from models.supplier import Supplier, SupplierEvaluation
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierEvaluationCreate
from typing import List, Optional
import uuid

def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
    """Create a new supplier"""
    db_supplier = Supplier(
        id=str(uuid.uuid4()),
        project_id=supplier.project_id,
        name=supplier.name,
        category=supplier.category,
        risk_rating=supplier.risk_rating,
        status=supplier.status,
        ai_metadata=supplier.ai_metadata
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def get_suppliers_by_project(db: Session, project_id: str) -> List[Supplier]:
    """Get all suppliers for a project"""
    return db.query(Supplier).filter(Supplier.project_id == project_id).all()

def get_supplier(db: Session, supplier_id: str, project_id: str) -> Optional[Supplier]:
    """Get a specific supplier"""
    return db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.project_id == project_id
    ).first()

def update_supplier(db: Session, supplier_id: str, supplier: SupplierUpdate, project_id: str) -> Optional[Supplier]:
    """Update a supplier"""
    db_supplier = get_supplier(db, supplier_id, project_id)
    if not db_supplier:
        return None
    
    update_data = supplier.model_dump(exclude_unset=True) if hasattr(supplier, 'model_dump') else supplier.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def create_supplier_evaluation(db: Session, evaluation: SupplierEvaluationCreate) -> SupplierEvaluation:
    """Create a supplier evaluation"""
    db_eval = SupplierEvaluation(
        id=str(uuid.uuid4()),
        supplier_id=evaluation.supplier_id,
        evaluation_text=evaluation.evaluation_text,
        score=evaluation.score,
        ai_metadata=evaluation.ai_metadata
    )
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)
    return db_eval

def get_supplier_evaluations(db: Session, supplier_id: str) -> List[SupplierEvaluation]:
    """Get all evaluations for a supplier"""
    return db.query(SupplierEvaluation).filter(
        SupplierEvaluation.supplier_id == supplier_id
    ).all()

