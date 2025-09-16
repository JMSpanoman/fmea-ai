from sqlalchemy.orm import Session
from models.project import Project
from schemas.project import ProjectCreate, ProjectUpdate
from typing import List, Optional

def create_project(db: Session, project: ProjectCreate, user_id: str) -> Project:
    """Create a new project"""
    db_project = Project(
        name=project.name,
        description=project.description,
        user_id=user_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_projects_by_user(db: Session, user_id: str) -> List[Project]:
    """Get all projects for a user"""
    return db.query(Project).filter(Project.user_id == user_id).all()

def get_project(db: Session, project_id: int, user_id: str) -> Optional[Project]:
    """Get a specific project by ID for a user"""
    return db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()

def update_project(db: Session, project_id: int, project: ProjectUpdate, user_id: str) -> Optional[Project]:
    """Update a project"""
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return None
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int, user_id: str) -> bool:
    """Delete a project"""
    db_project = get_project(db, project_id, user_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True
