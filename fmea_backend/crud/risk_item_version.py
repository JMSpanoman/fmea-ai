from sqlalchemy.orm import Session
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from schemas.risk_item import RiskItemVersionCreate, RiskItemVersionOut
from typing import List, Optional
import uuid

def _calculate_risk_score_iso14971(
    severity: Optional[int],
    probability_of_harm: Optional[int],
    detection: Optional[int] = None
) -> Optional[int]:
    """Calculate risk score using ISO 14971 approach"""
    if severity is not None and probability_of_harm is not None:
        # If detection is provided (FMEA style), use it; otherwise assume detection=1
        detection_factor = detection if detection is not None else 1
        return severity * probability_of_harm * detection_factor
    return None

def _determine_risk_level(risk_score: Optional[int]) -> Optional[str]:
    """Determine risk level based on risk score"""
    if risk_score is None:
        return None
    if risk_score >= 700:
        return "Critical"
    elif risk_score >= 400:
        return "High"
    elif risk_score >= 200:
        return "Medium"
    else:
        return "Low"

def create_risk_item_version(
    db: Session,
    risk_item_id: str,
    version_data: RiskItemVersionCreate,
    changed_by: str
) -> RiskItemVersion:
    """Create a new immutable version of a risk item"""
    # Get current version number
    current_version = db.query(RiskItemVersion).filter(
        RiskItemVersion.risk_item_id == risk_item_id
    ).order_by(RiskItemVersion.version_number.desc()).first()
    
    version_number = 1
    if current_version:
        version_number = current_version.version_number + 1
    
    # Normalize probability fields (backward compatibility)
    probability_of_harm = version_data.probability_of_harm
    if probability_of_harm is None and version_data.occurrence is not None:
        probability_of_harm = version_data.occurrence
    if probability_of_harm is None and version_data.probability is not None:
        probability_of_harm = version_data.probability
    
    # Calculate risk scores
    risk_score = _calculate_risk_score_iso14971(
        version_data.severity,
        probability_of_harm,
        version_data.detection
    )
    risk_level = _determine_risk_level(risk_score)
    
    residual_risk_score = None
    residual_risk_level = None
    if version_data.residual_severity is not None and version_data.residual_probability_of_harm is not None:
        residual_detection = version_data.residual_detection if version_data.residual_detection else 1
        residual_risk_score = version_data.residual_severity * version_data.residual_probability_of_harm * residual_detection
        residual_risk_level = _determine_risk_level(residual_risk_score)
    
    db_version = RiskItemVersion(
        id=str(uuid.uuid4()),
        risk_item_id=risk_item_id,
        version_number=version_number,
        hazard=version_data.hazard,
        hazardous_situation=version_data.hazardous_situation,
        harm=version_data.harm,
        failure_mode=version_data.failure_mode,
        sequence_of_events=version_data.sequence_of_events,
        severity=version_data.severity,
        probability_of_harm=probability_of_harm,
        occurrence=version_data.occurrence or probability_of_harm,
        detection=version_data.detection,
        probability=version_data.probability or probability_of_harm,  # Legacy
        impact=version_data.impact,  # Legacy
        risk_score=risk_score,
        risk_level=risk_level,
        inherent_safety=version_data.inherent_safety,
        protective_measures=version_data.protective_measures,
        information_for_safety=version_data.information_for_safety,
        control_measures_summary=version_data.control_measures_summary,
        residual_severity=version_data.residual_severity,
        residual_probability_of_harm=version_data.residual_probability_of_harm,
        residual_occurrence=version_data.residual_occurrence or version_data.residual_probability_of_harm,
        residual_detection=version_data.residual_detection,
        residual_risk_score=residual_risk_score,
        residual_risk_level=residual_risk_level,
        benefit_risk_summary=version_data.benefit_risk_summary,
        overall_residual_risk_conclusion=version_data.overall_residual_risk_conclusion,
        risk_acceptability=version_data.risk_acceptability,
        risk_rationale=version_data.risk_rationale,
        change_summary=version_data.change_summary,
        changed_by=changed_by,
        ai_metadata=version_data.ai_metadata
    )
    
    db.add(db_version)
    db.flush()
    
    # Update risk item's current_version_id
    risk_item = db.query(RiskItem).filter(RiskItem.id == risk_item_id).first()
    if risk_item:
        risk_item.current_version_id = db_version.id
        db.commit()
    else:
        db.commit()
    
    db.refresh(db_version)
    return db_version

def get_risk_item_versions(db: Session, risk_item_id: str) -> List[RiskItemVersion]:
    """Get all versions for a risk item"""
    return db.query(RiskItemVersion).filter(
        RiskItemVersion.risk_item_id == risk_item_id
    ).order_by(RiskItemVersion.version_number.desc()).all()

def get_risk_item_version(db: Session, version_id: str, risk_item_id: str) -> Optional[RiskItemVersion]:
    """Get a specific version"""
    return db.query(RiskItemVersion).filter(
        RiskItemVersion.id == version_id,
        RiskItemVersion.risk_item_id == risk_item_id
    ).first()

def get_current_version(db: Session, risk_item_id: str) -> Optional[RiskItemVersion]:
    """Get the current version of a risk item"""
    risk_item = db.query(RiskItem).filter(RiskItem.id == risk_item_id).first()
    if risk_item and risk_item.current_version_id:
        return db.query(RiskItemVersion).filter(
            RiskItemVersion.id == risk_item.current_version_id
        ).first()
    return None

