"""
Risk Knowledge Base API.

Four reusable libraries for medical device risk management:
- Hazard Library
- Harm Library
- Risk Control Library
- Verification Library

Designed for reference by FMEA entries, hazard analysis, and risk records;
supports future auto-generation of FMEA rows and risk analysis reports.
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import risk_knowledge_base as crud
from schemas import risk_knowledge_base as schemas

router = APIRouter(prefix="/risk-knowledge-base", tags=["Risk Knowledge Base"])


# ---------- Hazard Library ----------
@router.get("/hazards", response_model=list[schemas.HazardLibraryOut])
def list_hazards(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hazard library entries. Optional filters: is_active, category, search."""
    return crud.get_hazard_libraries(
        db, skip=skip, limit=limit, is_active=is_active, category=category, search=search
    )


@router.get("/hazards/{item_id}", response_model=schemas.HazardLibraryOut)
def get_hazard(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single hazard library entry by ID."""
    item = crud.get_hazard_library(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hazard library entry not found")
    return item


@router.post(
    "/hazards",
    response_model=schemas.HazardLibraryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_hazard(
    item: schemas.HazardLibraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hazard library entry."""
    return crud.create_hazard_library(db, item)


@router.put("/hazards/{item_id}", response_model=schemas.HazardLibraryOut)
def update_hazard(
    item_id: str,
    item: schemas.HazardLibraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a hazard library entry."""
    updated = crud.update_hazard_library(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Hazard library entry not found")
    return updated


@router.delete("/hazards/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hazard(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a hazard library entry."""
    if not crud.delete_hazard_library(db, item_id):
        raise HTTPException(status_code=404, detail="Hazard library entry not found")


# ---------- Harm Library ----------
@router.get("/harms", response_model=list[schemas.HarmLibraryOut])
def list_harms(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List harm library entries. Optional search on harm_id, harm_name, description, clinical_examples."""
    return crud.get_harm_libraries(db, skip=skip, limit=limit, search=search)


@router.get("/harms/{item_id}", response_model=schemas.HarmLibraryOut)
def get_harm(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single harm library entry by ID."""
    item = crud.get_harm_library(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Harm library entry not found")
    return item


@router.post(
    "/harms",
    response_model=schemas.HarmLibraryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_harm(
    item: schemas.HarmLibraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new harm library entry."""
    return crud.create_harm_library(db, item)


@router.put("/harms/{item_id}", response_model=schemas.HarmLibraryOut)
def update_harm(
    item_id: str,
    item: schemas.HarmLibraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a harm library entry."""
    updated = crud.update_harm_library(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Harm library entry not found")
    return updated


@router.delete("/harms/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_harm(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a harm library entry."""
    if not crud.delete_harm_library(db, item_id):
        raise HTTPException(status_code=404, detail="Harm library entry not found")


# ---------- Risk Control Library ----------
@router.get("/risk-controls", response_model=list[schemas.RiskControlLibraryOut])
def list_risk_controls(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    control_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List risk control library entries. control_type: design | protective | information."""
    return crud.get_risk_control_libraries(
        db, skip=skip, limit=limit, control_type=control_type, search=search
    )


@router.get("/risk-controls/{item_id}", response_model=schemas.RiskControlLibraryOut)
def get_risk_control(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single risk control library entry by ID."""
    item = crud.get_risk_control_library(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Risk control library entry not found")
    return item


@router.post(
    "/risk-controls",
    response_model=schemas.RiskControlLibraryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_risk_control(
    item: schemas.RiskControlLibraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new risk control library entry."""
    return crud.create_risk_control_library(db, item)


@router.put("/risk-controls/{item_id}", response_model=schemas.RiskControlLibraryOut)
def update_risk_control(
    item_id: str,
    item: schemas.RiskControlLibraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a risk control library entry."""
    updated = crud.update_risk_control_library(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Risk control library entry not found")
    return updated


@router.delete("/risk-controls/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_control(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a risk control library entry."""
    if not crud.delete_risk_control_library(db, item_id):
        raise HTTPException(status_code=404, detail="Risk control library entry not found")


# ---------- Verification Library ----------
@router.get("/verifications", response_model=list[schemas.VerificationLibraryOut])
def list_verifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List verification library entries. Optional search on verification_id, verification_method, description, etc."""
    return crud.get_verification_libraries(db, skip=skip, limit=limit, search=search)


@router.get("/verifications/{item_id}", response_model=schemas.VerificationLibraryOut)
def get_verification(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single verification library entry by ID."""
    item = crud.get_verification_library(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Verification library entry not found")
    return item


@router.post(
    "/verifications",
    response_model=schemas.VerificationLibraryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_verification(
    item: schemas.VerificationLibraryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new verification library entry."""
    return crud.create_verification_library(db, item)


@router.put("/verifications/{item_id}", response_model=schemas.VerificationLibraryOut)
def update_verification(
    item_id: str,
    item: schemas.VerificationLibraryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a verification library entry."""
    updated = crud.update_verification_library(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Verification library entry not found")
    return updated


@router.delete("/verifications/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_verification(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a verification library entry."""
    if not crud.delete_verification_library(db, item_id):
        raise HTTPException(status_code=404, detail="Verification library entry not found")
