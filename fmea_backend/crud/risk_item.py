from sqlalchemy.orm import Session
from models.risk_item import RiskItem
from models.risk_item_version import RiskItemVersion
from schemas.risk_item import RiskItemCreate, RiskItemUpdate, RiskItemVersionCreate
from crud import risk_item_version as version_crud
from typing import List, Optional
import uuid

def _calculate_risk_score(severity: Optional[int], probability: Optional[int], impact: Optional[int]) -> Optional[int]:
    """Calculate risk score from severity, probability, and impact"""
    if severity is not None and probability is not None and impact is not None:
        return severity * probability * impact
    return None

def _determine_risk_level(risk_score: Optional[int]) -> Optional[str]:
    """Determine risk level based on risk score"""
    if risk_score is None:
        return None
    if risk_score >= 700:  # 10 * 10 * 7
        return "Critical"
    elif risk_score >= 400:  # 10 * 8 * 5
        return "High"
    elif risk_score >= 200:  # 8 * 5 * 5
        return "Medium"
    else:
        return "Low"

def _generate_risk_key(db: Session, project_id: str) -> str:
    """Generate a unique risk_key for a project (e.g., R-001, R-002)"""
    # Get the highest existing risk_key number for this project
    existing_keys = db.query(RiskItem.risk_key).filter(
        RiskItem.project_id == project_id,
        RiskItem.risk_key.isnot(None)
    ).all()
    
    max_num = 0
    for (key,) in existing_keys:
        if key and key.startswith('R-'):
            try:
                num = int(key[2:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    # Generate next key
    next_num = max_num + 1
    return f"R-{next_num:03d}"

def create_risk_item(db: Session, risk_item: RiskItemCreate, created_by: Optional[str] = None) -> RiskItem:
    """Create a new risk item with auto-calculated risk score and level"""
    # Generate risk_key if not provided
    risk_key = getattr(risk_item, 'risk_key', None)
    if not risk_key:
        risk_key = _generate_risk_key(db, risk_item.project_id)
    
    db_risk_item = RiskItem(
        id=str(uuid.uuid4()),
        project_id=risk_item.project_id,
        fmea_row_id=risk_item.fmea_row_id,
        component_id=getattr(risk_item, "component_id", None),
        component_name=getattr(risk_item, "component_name", None),
        risk_key=risk_key,
        created_by=created_by,
        title=risk_item.title,
        description=risk_item.description,
        category=risk_item.category,
        risk_type=risk_item.risk_type,
        severity=risk_item.severity,
        probability=risk_item.probability,
        impact=risk_item.impact,
        mitigation_strategy=risk_item.mitigation_strategy,
        control_measures=risk_item.control_measures,
        residual_risk_score=risk_item.residual_risk_score,
        owner=risk_item.owner,
        status=risk_item.status or "open",
        priority=risk_item.priority,
        source=risk_item.source,
        detected_date=risk_item.detected_date,
        due_date=risk_item.due_date,
        ai_metadata=risk_item.ai_metadata
    )
    
    # Auto-calculate risk score and level
    db_risk_item.risk_score = _calculate_risk_score(
        db_risk_item.severity,
        db_risk_item.probability,
        db_risk_item.impact
    )
    db_risk_item.risk_level = _determine_risk_level(db_risk_item.risk_score)
    
    # Calculate residual risk level if residual risk score is provided
    if db_risk_item.residual_risk_score is not None:
        db_risk_item.residual_risk_level = _determine_risk_level(db_risk_item.residual_risk_score)
    
    db.add(db_risk_item)
    db.commit()
    db.refresh(db_risk_item)
    
    # Create initial version 1
    try:
        version_create = RiskItemVersionCreate(
            hazard=None,
            hazardous_situation=None,
            harm=None,
            severity=db_risk_item.severity,
            probability=db_risk_item.probability,
            probability_of_harm=db_risk_item.probability,
            impact=db_risk_item.impact,
            risk_rationale=None
        )
        version_crud.create_risk_item_version(
            db,
            db_risk_item.id,
            version_create,
            changed_by=created_by or "system",
            created_by=created_by
        )
    except Exception:
        # If version creation fails, risk item still created for backward compatibility
        pass
    
    return db_risk_item

def get_risk_items_by_project(db: Session, project_id: str) -> List[RiskItem]:
    """Get all risk items for a project"""
    return db.query(RiskItem).filter(RiskItem.project_id == project_id).all()

def get_risk_item(db: Session, risk_item_id: str, project_id: str) -> Optional[RiskItem]:
    """Get a specific risk item by ID"""
    return db.query(RiskItem).filter(
        RiskItem.id == risk_item_id,
        RiskItem.project_id == project_id
    ).first()

def update_risk_item(db: Session, risk_item_id: str, risk_item: RiskItemUpdate, project_id: str, changed_by: Optional[str] = None) -> Optional[RiskItem]:
    """Update a risk item by creating a new version (immutable versioning)"""
    db_risk_item = get_risk_item(db, risk_item_id, project_id)
    if not db_risk_item:
        return None
    
    # Get current version to create new version from
    current_version = version_crud.get_current_version(db, risk_item_id)
    
    # Pydantic v2 compatibility
    if hasattr(risk_item, 'model_dump'):
        update_data = risk_item.model_dump(exclude_unset=True)
    else:
        update_data = risk_item.dict(exclude_unset=True)
    
    # Create version data from current version + updates
    version_data_dict = {}
    if current_version:
        # Copy current version data
        version_data_dict = {
            'hazard': current_version.hazard,
            'hazardous_situation': current_version.hazardous_situation,
            'harm': current_version.harm,
            'failure_mode': current_version.failure_mode,
            'sequence_of_events': current_version.sequence_of_events,
            'severity': current_version.severity,
            'probability_of_harm': current_version.probability_of_harm,
            'occurrence': current_version.occurrence,
            'detection': current_version.detection,
            'probability': current_version.probability,
            'impact': current_version.impact,
            'inherent_safety': current_version.inherent_safety,
            'protective_measures': current_version.protective_measures,
            'information_for_safety': current_version.information_for_safety,
            'control_measures_summary': current_version.control_measures_summary,
            'residual_severity': current_version.residual_severity,
            'residual_probability_of_harm': current_version.residual_probability_of_harm,
            'residual_occurrence': current_version.residual_occurrence,
            'residual_detection': current_version.residual_detection,
            'benefit_risk_summary': current_version.benefit_risk_summary,
            'overall_residual_risk_conclusion': current_version.overall_residual_risk_conclusion,
            'risk_acceptability': current_version.risk_acceptability,
            'risk_rationale': current_version.risk_rationale,
        }
    
    # Apply updates (prioritize ISO 14971 fields if provided)
    version_data_dict.update(update_data)
    
    # Update legacy fields on risk_item for backward compatibility
    for field in ['title', 'description', 'category', 'risk_type', 'owner', 'status', 'priority', 'source', 'detected_date', 'due_date', 'ai_metadata', 'component_id', 'component_name']:
        if field in update_data:
            setattr(db_risk_item, field, update_data[field])
    
    # Legacy risk assessment fields (for backward compatibility)
    if 'severity' in update_data:
        db_risk_item.severity = update_data['severity']
    if 'probability' in update_data:
        db_risk_item.probability = update_data['probability']
    if 'impact' in update_data:
        db_risk_item.impact = update_data['impact']
    
    # Recalculate legacy risk score
    if any(field in update_data for field in ['severity', 'probability', 'impact']):
        db_risk_item.risk_score = _calculate_risk_score(
            db_risk_item.severity,
            db_risk_item.probability,
            db_risk_item.impact
        )
        db_risk_item.risk_level = _determine_risk_level(db_risk_item.risk_score)
    
    if 'residual_risk_score' in update_data and update_data['residual_risk_score'] is not None:
        db_risk_item.residual_risk_score = update_data['residual_risk_score']
        db_risk_item.residual_risk_level = _determine_risk_level(db_risk_item.residual_risk_score)
    
    # Auto-set closed_date if status is changed to closed
    if 'status' in update_data and db_risk_item.status == "closed" and db_risk_item.closed_date is None:
        from datetime import datetime
        db_risk_item.closed_date = datetime.utcnow()
    
    # Create new version (immutable snapshot)
    try:
        version_create = RiskItemVersionCreate(**version_data_dict)
        version_crud.create_risk_item_version(
            db,
            risk_item_id,
            version_create,
            changed_by=changed_by or "system",
            created_by=changed_by
        )
    except Exception as e:
        # If version creation fails, still commit the legacy update for backward compatibility
        pass
    
    db.commit()
    db.refresh(db_risk_item)
    return db_risk_item

def delete_risk_item(db: Session, risk_item_id: str, project_id: str) -> bool:
    """Delete a risk item"""
    db_risk_item = get_risk_item(db, risk_item_id, project_id)
    if not db_risk_item:
        return False
    
    db.delete(db_risk_item)
    db.commit()
    return True

def get_risk_items_by_status(db: Session, project_id: str, status: str) -> List[RiskItem]:
    """Get all risk items for a project by status"""
    return db.query(RiskItem).filter(
        RiskItem.project_id == project_id,
        RiskItem.status == status
    ).all()

def get_risk_items_by_category(db: Session, project_id: str, category: str) -> List[RiskItem]:
    """Get all risk items for a project by category"""
    return db.query(RiskItem).filter(
        RiskItem.project_id == project_id,
        RiskItem.category == category
    ).all()

