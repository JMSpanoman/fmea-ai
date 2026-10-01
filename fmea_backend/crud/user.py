from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User, PLAN_LITE
from typing import Optional
import uuid
from datetime import datetime, timedelta, timezone

def get_user_by_auth0_id(db: Session, auth0_id: str) -> Optional[User]:
    """Get user by Auth0 ID"""
    return db.query(User).filter(User.auth0_id == auth0_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID (UUID)"""
    return db.query(User).filter(User.id == user_id).first()

def create_user_from_auth0(db: Session, auth0_id: str, email: str, *, start_trial: bool = False) -> Optional[User]:
    """Create a new user from Auth0 token"""
    try:
        # Ensure email is not empty (use auth0_id as fallback)
        if not email or email.strip() == "":
            email = f"{auth0_id}@auth0.local"
        
        now = datetime.now(timezone.utc) if start_trial else None
        db_user = User(
            id=str(uuid.uuid4()),
            auth0_id=auth0_id,
            email=email,
            plan=PLAN_LITE,
            trial_started_at=now,
            trial_ends_at=now + timedelta(days=14) if now else None,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        # Idempotency: if the user already exists (common in dev-login / repeated /auth/me),
        # return the existing record instead of failing auth.
        db.rollback()
        # Email is mutable and is not proof of ownership of an existing account.
        # Only the verified identity provider subject may recover this user.
        existing = get_user_by_auth0_id(db, auth0_id)
        if existing:
            # Best-effort keep email in sync
            try:
                if email and getattr(existing, "email", None) != email:
                    existing.email = email
                    db.add(existing)
                    db.commit()
                    db.refresh(existing)
            except Exception:
                db.rollback()
            return existing
        return None
    except Exception as e:
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating user from Auth0: {str(e)}", exc_info=True)
        return None

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()
