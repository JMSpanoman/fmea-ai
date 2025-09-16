from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import verify_token
from database import get_db
from schemas.fmea import FMEAOut
from crud.fmea import get_fmeas_for_project

router = APIRouter()

@router.get("/{project_id}/fmeas", response_model=List[FMEAOut])
def get_fmeas(project_id: int, db: Session = Depends(get_db), token_data=Depends(verify_token)):
    user_id = str(token_data.get("sub") or "dev-user-123")
    fmeas = get_fmeas_for_project(db, project_id, user_id)
    return fmeas
