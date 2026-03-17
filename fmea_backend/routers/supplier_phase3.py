from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import supplier as supplier_schemas
from crud import supplier_phase3 as supplier_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Supplier Quality Phase 3"], dependencies=[Depends(require_pro)])

@router.get("/suppliers", response_model=List[supplier_schemas.SupplierOut])
def get_suppliers(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all suppliers for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return supplier_crud.get_suppliers_by_project(db, project_id)

@router.post("/suppliers", response_model=supplier_schemas.SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(
    project_id: str,
    supplier: supplier_schemas.SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new supplier"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(supplier, 'model_copy'):
        supplier = supplier.model_copy(update={'project_id': project_id})
    else:
        supplier_dict = supplier.dict() if hasattr(supplier, 'dict') else supplier.model_dump()
        supplier_dict['project_id'] = project_id
        supplier = supplier_schemas.SupplierCreate(**supplier_dict)
    
    return supplier_crud.create_supplier(db, supplier)

@router.post("/suppliers/{supplier_id}/evaluate", response_model=supplier_schemas.SupplierEvaluationOut, status_code=status.HTTP_201_CREATED)
def evaluate_supplier(
    project_id: str,
    supplier_id: str,
    evaluation: supplier_schemas.SupplierEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a supplier evaluation"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    supplier = supplier_crud.get_supplier(db, supplier_id, project_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Ensure supplier_id matches
    if hasattr(evaluation, 'model_copy'):
        evaluation = evaluation.model_copy(update={'supplier_id': supplier_id})
    else:
        eval_dict = evaluation.dict() if hasattr(evaluation, 'dict') else evaluation.model_dump()
        eval_dict['supplier_id'] = supplier_id
        evaluation = supplier_schemas.SupplierEvaluationCreate(**eval_dict)
    
    return supplier_crud.create_supplier_evaluation(db, evaluation)

