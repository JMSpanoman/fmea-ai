from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User
from schemas.user import UserCreate, UserUpdate
from auth.security import get_password_hash, verify_password
from typing import Optional
from datetime import datetime

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        company=user_data.company,
        department=user_data.department,
        phone=user_data.phone,
        bio=user_data.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

def update_last_login(db: Session, user_id: int) -> None:
    """Update user's last login timestamp"""
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True

def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """Change user password"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    if not verify_password(current_password, user.hashed_password):
        return False
    
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()
    return True

def verify_user(db: Session, user_id: int) -> bool:
    """Verify a user account"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_verified = True
    user.updated_at = datetime.utcnow()
    db.commit()
    return True

def deactivate_user(db: Session, user_id: int) -> bool:
    """Deactivate a user account"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    return True

def activate_user(db: Session, user_id: int) -> bool:
    """Activate a user account"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.commit()
    return True

def change_user_role(db: Session, user_id: int, new_role: str) -> bool:
    """Change user role"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.role = new_role
    user.updated_at = datetime.utcnow()
    db.commit()
    return True 