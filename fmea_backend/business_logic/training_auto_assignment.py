"""
Business Logic for Training Auto-Assignment
Automatically assigns training when documents are approved
"""
import logging
from sqlalchemy.orm import Session
from crud import training as training_crud
from crud import project as project_crud
from typing import List

logger = logging.getLogger(__name__)

def auto_assign_training_on_document_approval(db: Session, document_id: str, project_id: str) -> List[str]:
    """
    Automatically assign training to all users in a project when a document is approved
    Returns list of user IDs who received training assignments
    """
    # Get project to find team members
    # In production, this would query a project_team or project_members table
    # For now, we'll get the project owner
    # Note: Passing empty string for user_id is not ideal, but needed for this function
    # In production, this should accept user_id parameter or query differently
    try:
        # Try to get project - this will fail if project doesn't exist
        # We need a way to get project without user_id check for this use case
        from models.project import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return []
    
    assigned_user_ids = []
    
    # Assign to project owner (user_id)
    try:
        training_crud.assign_training(db, project.user_id, document_id)
        assigned_user_ids.append(project.user_id)
    except Exception as e:
        logger.error(f"Error assigning training to project owner: {e}")
    
    # In production, also assign to all project team members
    # team_members = get_project_team_members(db, project_id)
    # for member in team_members:
    #     try:
    #         training_crud.assign_training(db, member.user_id, document_id)
    #         assigned_user_ids.append(member.user_id)
    #     except Exception as e:
    #         print(f"Error assigning training to {member.user_id}: {e}")
    
    return assigned_user_ids

