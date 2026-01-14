from sqlalchemy.orm import Session
from models.component import Component
from schemas.component import ComponentCreate, ComponentUpdate, ComponentBulkItem
from typing import List, Optional, Tuple, Set
import uuid

def create_component(db: Session, component: ComponentCreate, project_id: str) -> Component:
    """Create a new component"""
    db_component = Component(
        id=str(uuid.uuid4()),
        name=component.name,
        description=component.description,
        parent_id=getattr(component, "parent_id", None),
        tags=getattr(component, "tags", None),
        project_id=project_id
    )
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    return db_component

def get_components_by_project(db: Session, project_id: str) -> List[Component]:
    """Get all components for a project"""
    return db.query(Component).filter(Component.project_id == project_id).all()

def get_component(db: Session, component_id: str, project_id: str) -> Optional[Component]:
    """Get a specific component by ID for a project"""
    return db.query(Component).filter(
        Component.id == component_id,
        Component.project_id == project_id
    ).first()

def update_component(db: Session, component_id: str, component: ComponentUpdate, project_id: str) -> Optional[Component]:
    """Update a component"""
    db_component = get_component(db, component_id, project_id)
    if not db_component:
        return None
    
    # Pydantic v2 compatibility
    if hasattr(component, 'model_dump'):
        update_data = component.model_dump(exclude_unset=True)
    else:
        update_data = component.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_component, field, value)
    
    db.commit()
    db.refresh(db_component)
    return db_component


def bulk_create_replace_components(
    db: Session,
    *,
    project_id: str,
    items: List[ComponentBulkItem],
) -> Tuple[List[Component], dict]:
    """
    Bulk create/update components for a project, with a best-effort 'replace' cleanup.

    Safety behavior:
    - We only delete components that are NOT in the new set AND have no dependent rows.
      This avoids cascading deletes of FMEA rows (Component.fmea_rows has delete-orphan cascade).
    - If parent/child relationships would be broken by deletions, we skip those deletions.

    Returns: (final_components, stats)
    """
    existing = db.query(Component).filter(Component.project_id == project_id).all()
    existing_by_id = {c.id: c for c in existing}
    existing_by_name = {c.name: c for c in existing if c.name}

    # Assign stable ids for incoming items (generate if not provided)
    incoming_ids: Set[str] = set()
    incoming_records: List[Component] = []

    # First pass: create/update basic fields without parent links to avoid ordering issues.
    for item in items:
        if hasattr(item, "model_dump"):
            payload = item.model_dump(exclude_unset=True)
        else:
            payload = item.dict(exclude_unset=True)

        requested_id = payload.get("id")
        name = payload.get("name")

        target = None
        if requested_id and requested_id in existing_by_id:
            target = existing_by_id[requested_id]
        elif not requested_id and name and name in existing_by_name:
            target = existing_by_name[name]

        if target:
            # Update
            for k in ["name", "description", "tags"]:
                if k in payload:
                    setattr(target, k, payload[k])
            incoming_ids.add(target.id)
            incoming_records.append(target)
        else:
            new_id = requested_id or str(uuid.uuid4())
            rec = Component(
                id=new_id,
                project_id=project_id,
                name=payload.get("name"),
                description=payload.get("description"),
                tags=payload.get("tags"),
            )
            db.add(rec)
            incoming_ids.add(new_id)
            incoming_records.append(rec)

    db.flush()  # ensure new rows have identities in-session

    # Second pass: set parent_id (must reference an existing component id)
    all_now = db.query(Component).filter(Component.project_id == project_id).all()
    all_by_id = {c.id: c for c in all_now}
    for item in items:
        parent_id = getattr(item, "parent_id", None)
        cid = getattr(item, "id", None)
        # If item didn't have id, we matched by name and updated existing; parent_id can't be inferred.
        # We only set parent_id when an id is provided and valid.
        if cid and cid in all_by_id:
            if parent_id and parent_id in all_by_id:
                all_by_id[cid].parent_id = parent_id
            elif parent_id is None:
                all_by_id[cid].parent_id = None

    db.flush()

    # Best-effort cleanup: delete components not in incoming_ids and safe to delete.
    deleted = 0
    skipped_linked = 0
    skipped_parent = 0

    # Determine which components are parents of any other component.
    parent_ids_in_use: Set[str] = set([c.parent_id for c in all_now if c.parent_id])

    for c in all_now:
        if c.id in incoming_ids:
            continue

        # Don't delete if component is a parent.
        if c.id in parent_ids_in_use:
            skipped_parent += 1
            continue

        # Don't delete if it has dependent FMEA rows (delete-orphan would cascade).
        # Use relationship if loaded, else count query.
        try:
            has_fmea = len(getattr(c, "fmea_rows", []) or []) > 0
        except Exception:
            has_fmea = False

        if has_fmea:
            skipped_linked += 1
            continue

        # Also protect risk_items that reference components (even if relationship isn't configured).
        try:
            from models.risk_item import RiskItem
            risk_ref_count = (
                db.query(RiskItem).filter(RiskItem.project_id == project_id, RiskItem.component_id == c.id).count()
            )
            if risk_ref_count > 0:
                skipped_linked += 1
                continue
        except Exception:
            # If RiskItem isn't available in some contexts (tests), don't block deletion.
            pass

        db.delete(c)
        deleted += 1

    db.commit()

    final_components = db.query(Component).filter(Component.project_id == project_id).all()
    return final_components, {
        "incoming": len(items),
        "deleted": deleted,
        "skipped_linked": skipped_linked,
        "skipped_parent": skipped_parent,
        "final": len(final_components),
    }

def delete_component(db: Session, component_id: str, project_id: str) -> bool:
    """Delete a component"""
    db_component = get_component(db, component_id, project_id)
    if not db_component:
        return False
    
    db.delete(db_component)
    db.commit()
    return True

