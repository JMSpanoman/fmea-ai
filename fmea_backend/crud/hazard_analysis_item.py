"""
CRUD for HazardAnalysisItem — list, get, create, update, delete.
Preserves backward compatibility: old code using risk_item_versions still works.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from models.hazard_analysis_item import HazardAnalysisItem
from schemas.hazard_analysis_item import HazardAnalysisItemCreate, HazardAnalysisItemUpdate


def create_hazard_analysis_item(
    db: Session,
    payload: HazardAnalysisItemCreate,
    created_by: Optional[str] = None,
) -> HazardAnalysisItem:
    data = payload.model_dump(exclude_unset=True)
    if created_by:
        data["created_by"] = created_by
    item = HazardAnalysisItem(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_hazard_analysis_item(db: Session, item_id: str) -> Optional[HazardAnalysisItem]:
    return db.query(HazardAnalysisItem).filter(HazardAnalysisItem.id == item_id).first()


def list_hazard_analysis_items(
    db: Session,
    project_id: str,
    component_id: Optional[str] = None,
    device_id: Optional[str] = None,
    approval_status: Optional[str] = None,
    hazard_category: Optional[str] = None,
    include_draft: bool = True,
    skip: int = 0,
    limit: int = 500,
) -> List[HazardAnalysisItem]:
    q = db.query(HazardAnalysisItem).filter(HazardAnalysisItem.project_id == project_id)
    if component_id:
        q = q.filter(HazardAnalysisItem.component_id == component_id)
    if device_id:
        q = q.filter(HazardAnalysisItem.device_id == device_id)
    if approval_status:
        q = q.filter(HazardAnalysisItem.approval_status == approval_status)
    if hazard_category:
        q = q.filter(HazardAnalysisItem.hazard_category == hazard_category)
    if not include_draft:
        q = q.filter(HazardAnalysisItem.approval_status != "draft")
    q = q.order_by(HazardAnalysisItem.risk_key, HazardAnalysisItem.version_no.desc())
    return q.offset(skip).limit(limit).all()


def update_hazard_analysis_item(
    db: Session,
    item_id: str,
    payload: HazardAnalysisItemUpdate,
) -> Optional[HazardAnalysisItem]:
    item = get_hazard_analysis_item(db, item_id)
    if not item:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


def delete_hazard_analysis_item(db: Session, item_id: str) -> bool:
    item = get_hazard_analysis_item(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def approve_hazard_analysis_item(
    db: Session,
    item_id: str,
    approved_by: str,
) -> Optional[HazardAnalysisItem]:
    item = get_hazard_analysis_item(db, item_id)
    if not item:
        return None
    from datetime import datetime, timezone
    item.approval_status = "approved"
    item.approved_by = approved_by
    item.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item
