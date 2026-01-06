from sqlalchemy.orm import Session
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate
from typing import List, Optional
import uuid

def create_project(db: Session, project: ProjectCreate, user_id: str) -> Project:
    """Create a new project"""
    try:
        db_project = Project(
            id=str(uuid.uuid4()),
            name=project.name,
            description=project.description,
            user_id=user_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Database error creating project: {str(e)}", exc_info=True)
        raise

def get_projects_by_user(db: Session, user_id: str) -> List[Project]:
    """Get all projects for a user"""
    return db.query(Project).filter(Project.user_id == user_id).all()

def get_project(db: Session, project_id: str, user_id: str) -> Optional[Project]:
    """Get a specific project by ID for a user"""
    return db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

def update_project(db: Session, project_id: str, project: ProjectUpdate, user_id: str) -> Optional[Project]:
    """Update a project"""
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return None
    
    # Pydantic v2 compatibility
    if hasattr(project, 'model_dump'):
        update_data = project.model_dump(exclude_unset=True)
    else:
        update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str, user_id: str) -> bool:
    """Delete a project"""
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True
