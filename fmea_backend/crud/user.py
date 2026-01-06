from sqlalchemy.orm import Session
from models.user import User
from typing import Optional
import uuid

def get_user_by_auth0_id(db: Session, auth0_id: str) -> Optional[User]:
    """Get user by Auth0 ID"""
    return db.query(User).filter(User.auth0_id == auth0_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID (UUID)"""
    return db.query(User).filter(User.id == user_id).first()

def create_user_from_auth0(db: Session, auth0_id: str, email: str) -> Optional[User]:
    """Create a new user from Auth0 token"""
    try:
        # Ensure email is not empty (use auth0_id as fallback)
        if not email or email.strip() == "":
            email = f"{auth0_id}@auth0.local"
        
        db_user = User(
            id=str(uuid.uuid4()),
            auth0_id=auth0_id,
            email=email
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating user from Auth0: {str(e)}", exc_info=True)
        return None

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()
