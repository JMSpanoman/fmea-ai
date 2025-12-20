from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from auth.dependencies import verify_token
from database import get_db
from schemas.fmea import FMEARowOut
from crud.fmea import get_fmea_rows_by_project

router = APIRouter()

@router.get("/{project_id}/fmeas", response_model=List[FMEARowOut])
def get_fmeas(project_id: int, db: Session = Depends(get_db), token_data=Depends(verify_token)):
    user_id = str(token_data.get("sub") or "dev-user-123")
    fmeas = get_fmea_rows_by_project(db, str(project_id))
    return fmeas
