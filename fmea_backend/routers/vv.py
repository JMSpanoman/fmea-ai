from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import vv as vv_schemas
from crud import vv as vv_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["V&V"])

@router.get("/vv-tests", response_model=List[vv_schemas.VVTestOut])
def get_vv_tests(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all V&V tests for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return vv_crud.get_vv_tests_by_project(db, project_id)

@router.post("/vv-tests", response_model=vv_schemas.VVTestOut, status_code=status.HTTP_201_CREATED)
def create_vv_test(
    project_id: str,
    vv_test: vv_schemas.VVTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new V&V test"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(vv_test, 'model_copy'):
        vv_test = vv_test.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        vv_test_dict = vv_test.dict() if hasattr(vv_test, 'dict') else vv_test.model_dump()
        vv_test_dict['project_id'] = project_id
        vv_test = vv_schemas.VVTestCreate(**vv_test_dict)
    
    return vv_crud.create_vv_test(db, vv_test)

@router.get("/vv-tests/{vv_test_id}", response_model=vv_schemas.VVTestOut)
def get_vv_test(
    project_id: str,
    vv_test_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific V&V test"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    vv_test = vv_crud.get_vv_test(db, vv_test_id, project_id)
    if not vv_test:
        raise HTTPException(status_code=404, detail="V&V test not found")
    
    return vv_test

