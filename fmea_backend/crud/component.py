from sqlalchemy.orm import Session
from models.component import Component
from schemas.component import ComponentCreate, ComponentUpdate
from typing import List, Optional
import uuid

def create_component(db: Session, component: ComponentCreate, project_id: str) -> Component:
    """Create a new component"""
    db_component = Component(
        id=str(uuid.uuid4()),
        name=component.name,
        description=component.description,
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

def delete_component(db: Session, component_id: str, project_id: str) -> bool:
    """Delete a component"""
    db_component = get_component(db, component_id, project_id)
    if not db_component:
        return False
    
    db.delete(db_component)
    db.commit()
    return True

