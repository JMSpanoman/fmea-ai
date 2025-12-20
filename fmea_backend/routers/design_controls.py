from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import design_control as dc_schemas
from crud import design_control as dc_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Design Controls"])

@router.get("/design-inputs", response_model=List[dc_schemas.DesignInputOut])
def get_design_inputs(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all design inputs for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return dc_crud.get_design_inputs_by_project(db, project_id)

@router.post("/design-inputs", response_model=dc_schemas.DesignInputOut, status_code=status.HTTP_201_CREATED)
def create_design_input(
    project_id: str,
    design_input: dc_schemas.DesignInputCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new design input"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(design_input, 'model_copy'):
        design_input = design_input.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        design_input_dict = design_input.dict() if hasattr(design_input, 'dict') else design_input.model_dump()
        design_input_dict['project_id'] = project_id
        design_input = dc_schemas.DesignInputCreate(**design_input_dict)
    
    return dc_crud.create_design_input(db, design_input)

@router.get("/design-inputs/{design_input_id}", response_model=dc_schemas.DesignInputOut)
def get_design_input(
    project_id: str,
    design_input_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific design input"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    design_input = dc_crud.get_design_input(db, design_input_id, project_id)
    if not design_input:
        raise HTTPException(status_code=404, detail="Design input not found")
    
    return design_input

@router.get("/design-outputs", response_model=List[dc_schemas.DesignOutputOut])
def get_design_outputs(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all design outputs for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return dc_crud.get_design_outputs_by_project(db, project_id)

@router.post("/design-outputs", response_model=dc_schemas.DesignOutputOut, status_code=status.HTTP_201_CREATED)
def create_design_output(
    project_id: str,
    design_output: dc_schemas.DesignOutputCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new design output"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(design_output, 'model_copy'):
        design_output = design_output.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        design_output_dict = design_output.dict() if hasattr(design_output, 'dict') else design_output.model_dump()
        design_output_dict['project_id'] = project_id
        design_output = dc_schemas.DesignOutputCreate(**design_output_dict)
    
    return dc_crud.create_design_output(db, design_output)

@router.get("/design-outputs/{design_output_id}", response_model=dc_schemas.DesignOutputOut)
def get_design_output(
    project_id: str,
    design_output_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific design output"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    design_output = dc_crud.get_design_output(db, design_output_id, project_id)
    if not design_output:
        raise HTTPException(status_code=404, detail="Design output not found")
    
    return design_output

