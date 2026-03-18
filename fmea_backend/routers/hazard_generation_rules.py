"""
Hazard Generation Rules API (SmartRisk Phase 2).
Admin-editable rules: component/interface type → hazard library.
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import hazard_generation_rule as crud
from schemas import hazard_generation_rule as schemas

router = APIRouter(prefix="/hazard-generation-rules", tags=["Hazard Generation Rules"])


@router.get("", response_model=list[schemas.HazardGenerationRuleOut])
def list_rules(
    trigger_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hazard generation rules. Optional filters: trigger_type, is_active."""
    return crud.list_rules(
        db, trigger_type=trigger_type, is_active=is_active, skip=skip, limit=limit
    )


@router.get("/{rule_id}", response_model=schemas.HazardGenerationRuleOut)
def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get one rule."""
    row = crud.get_rule(db, rule_id)
    if not row:
        raise HTTPException(status_code=404, detail="Rule not found")
    return row


@router.post("", response_model=schemas.HazardGenerationRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    body: schemas.HazardGenerationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a hazard generation rule."""
    return crud.create_rule(db, body)


@router.patch("/{rule_id}", response_model=schemas.HazardGenerationRuleOut)
def update_rule(
    rule_id: str,
    body: schemas.HazardGenerationRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a rule."""
    updated = crud.update_rule(db, rule_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a rule."""
    if not crud.delete_rule(db, rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
