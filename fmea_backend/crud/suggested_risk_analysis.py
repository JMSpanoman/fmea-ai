"""CRUD for suggested risk analysis (suggestion sets and suggested_* rows)."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.suggested_risk_analysis import (
    RiskAnalysisSuggestionSet,
    SuggestedFailureMode,
    SuggestedHazard as SuggestedHazardRow,
    SuggestedHazardousSituation,
    SuggestedHarm,
    SuggestedControl,
    SuggestedVerificationMethod,
)


def _suggestion_set_belongs_to_component(
    db: Session, set_id: str, project_id: str, component_id: str
) -> bool:
    s = get_suggestion_set(db, set_id)
    if not s:
        return False
    return (
        s.source_type == "component"
        and s.source_id == component_id
        and s.project_id == project_id
    )


def delete_suggestions_by_source(
    db: Session,
    source_type: str,
    source_id: str,
    architecture_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> int:
    """
    Delete all suggestion sets for a given source (node, interface, or component).
    Used for regeneration. Returns number of sets deleted.
    """
    q = db.query(RiskAnalysisSuggestionSet).filter(
        RiskAnalysisSuggestionSet.source_type == source_type,
        RiskAnalysisSuggestionSet.source_id == source_id,
    )
    if architecture_id is not None:
        q = q.filter(RiskAnalysisSuggestionSet.architecture_id == architecture_id)
    if project_id is not None:
        q = q.filter(RiskAnalysisSuggestionSet.project_id == project_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.commit()
    return count


def delete_suggestions_by_component(
    db: Session, project_id: str, component_id: str
) -> int:
    """Delete all suggestion sets for a project component. Returns number deleted."""
    return delete_suggestions_by_source(
        db, source_type="component", source_id=component_id, project_id=project_id
    )


def delete_suggestions_by_architecture(
    db: Session, architecture_id: str
) -> int:
    """Delete all suggestion sets for an architecture. Returns number deleted."""
    count = db.query(RiskAnalysisSuggestionSet).filter(
        RiskAnalysisSuggestionSet.architecture_id == architecture_id
    ).count()
    db.query(RiskAnalysisSuggestionSet).filter(
        RiskAnalysisSuggestionSet.architecture_id == architecture_id
    ).delete(synchronize_session=False)
    db.commit()
    return count


def list_suggestion_sets_by_source(
    db: Session,
    source_type: str,
    source_id: str,
    architecture_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[RiskAnalysisSuggestionSet]:
    """List suggestion sets for a given source."""
    q = db.query(RiskAnalysisSuggestionSet).filter(
        RiskAnalysisSuggestionSet.source_type == source_type,
        RiskAnalysisSuggestionSet.source_id == source_id,
    )
    if architecture_id is not None:
        q = q.filter(RiskAnalysisSuggestionSet.architecture_id == architecture_id)
    if project_id is not None:
        q = q.filter(RiskAnalysisSuggestionSet.project_id == project_id)
    return q.order_by(RiskAnalysisSuggestionSet.created_at).all()


def list_suggestion_sets_by_component(
    db: Session, project_id: str, component_id: str
) -> List[RiskAnalysisSuggestionSet]:
    """List suggestion sets for a project component."""
    return list_suggestion_sets_by_source(
        db, source_type="component", source_id=component_id, project_id=project_id
    )


def list_suggestion_sets_by_architecture(
    db: Session, architecture_id: str
) -> List[RiskAnalysisSuggestionSet]:
    """List all suggestion sets for an architecture."""
    return (
        db.query(RiskAnalysisSuggestionSet)
        .filter(RiskAnalysisSuggestionSet.architecture_id == architecture_id)
        .order_by(RiskAnalysisSuggestionSet.source_type, RiskAnalysisSuggestionSet.source_id)
        .all()
    )


def get_suggestion_set(
    db: Session, suggestion_set_id: str
) -> Optional[RiskAnalysisSuggestionSet]:
    return (
        db.query(RiskAnalysisSuggestionSet)
        .filter(RiskAnalysisSuggestionSet.id == suggestion_set_id)
        .first()
    )


def delete_suggestion_set(db: Session, suggestion_set_id: str) -> bool:
    """Delete a single suggestion set (and its child rows via cascade). Returns True if deleted."""
    row = get_suggestion_set(db, suggestion_set_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def update_suggested_hazard_library(
    db: Session, suggested_hazard_id: str, hazard_library_id: Optional[str]
) -> Optional[SuggestedHazardRow]:
    row = db.query(SuggestedHazardRow).filter(SuggestedHazardRow.id == suggested_hazard_id).first()
    if not row:
        return None
    row.hazard_library_id = hazard_library_id
    db.commit()
    db.refresh(row)
    return row


def update_suggested_harm_library(
    db: Session, suggested_harm_id: str, harm_library_id: Optional[str]
) -> Optional[SuggestedHarm]:
    row = db.query(SuggestedHarm).filter(SuggestedHarm.id == suggested_harm_id).first()
    if not row:
        return None
    row.harm_library_id = harm_library_id
    db.commit()
    db.refresh(row)
    return row


def update_suggested_control_library(
    db: Session, suggested_control_id: str, risk_control_library_id: Optional[str]
) -> Optional[SuggestedControl]:
    row = db.query(SuggestedControl).filter(SuggestedControl.id == suggested_control_id).first()
    if not row:
        return None
    row.risk_control_library_id = risk_control_library_id
    db.commit()
    db.refresh(row)
    return row


def update_suggested_verification_library(
    db: Session, suggested_verification_id: str, verification_library_id: Optional[str]
) -> Optional[SuggestedVerificationMethod]:
    row = db.query(SuggestedVerificationMethod).filter(
        SuggestedVerificationMethod.id == suggested_verification_id
    ).first()
    if not row:
        return None
    row.verification_library_id = verification_library_id
    db.commit()
    db.refresh(row)
    return row


def get_suggested_hazard(db: Session, suggested_hazard_id: str) -> Optional[SuggestedHazardRow]:
    return db.query(SuggestedHazardRow).filter(SuggestedHazardRow.id == suggested_hazard_id).first()


def get_suggested_harm(db: Session, suggested_harm_id: str) -> Optional[SuggestedHarm]:
    return db.query(SuggestedHarm).filter(SuggestedHarm.id == suggested_harm_id).first()


def get_suggested_control(db: Session, suggested_control_id: str) -> Optional[SuggestedControl]:
    return db.query(SuggestedControl).filter(SuggestedControl.id == suggested_control_id).first()


def get_suggested_verification(
    db: Session, suggested_verification_id: str
) -> Optional[SuggestedVerificationMethod]:
    return db.query(SuggestedVerificationMethod).filter(
        SuggestedVerificationMethod.id == suggested_verification_id
    ).first()
