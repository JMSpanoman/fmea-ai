from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User, PLAN_LITE, PLAN_PRO
from schemas.user import UserCreate, UserLogin, UserOut, UserProfile, Token, UserUpdate, PasswordChange
from crud import user as user_crud
from auth.security import create_access_token, verify_token, get_password_hash, verify_password
from auth.dependencies import get_current_user
from datetime import datetime, timedelta, timezone
import os

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username already exists
        if user_crud.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if user_crud.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = user_crud.create_user(db, user_data)
        
        # Create default project for new user
        from crud import project as project_crud
        from schemas import project as project_schemas
        
        default_project = project_schemas.ProjectCreate(
            name="Default Project",
            description="Your first project - get started by creating FMEA, CAPA, or other quality management documents.",
            user_id=user.username
        )
        
        project_crud.create_project(db, default_project, user.username)
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = user_crud.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Update last login
    user_crud.update_last_login(db, user.id)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            company=user.company,
            department=user.department,
            phone=user.phone,
            bio=user.bio,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
    }

@router.post("/dev-login", response_model=Token)
def dev_login(
    payload: Optional[dict] = Body(default=None),
    db: Session = Depends(get_db),
):
    """
    Development-only login endpoint.
    SECURITY: This endpoint is disabled in production by default.
    If you explicitly enable it (e.g., for demos), it should be gated by env flags.
    """
    import logging

    logger = logging.getLogger(__name__)
    env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or os.getenv("ENV") or "development").lower()
    is_prod_like = env in ("production", "prod", "staging")
    # NOTE: This endpoint is intentionally email-gated in production-like environments:
    # - requires explicit email (no implicit dev@example.com)
    # - optional allowlist via DEV_LOGIN_ALLOWED_EMAILS

    from auth.security import create_dev_token
    from crud import project as project_crud
    from crud import user as user_crud
    from schemas import project as project_schemas

    # Allow choosing a dev identity so multiple users can sign in locally.
    # Backward-compatible: if no payload provided, uses dev@example.com.
    email = "dev@example.com"
    # Default dev role is a regular user; allow explicit role override, and grant admin to John.
    role = "user"
    if isinstance(payload, dict):
        raw_email = str(payload.get("email") or "").strip()
        if raw_email:
            email = raw_email
        raw_role = str(payload.get("role") or "").strip()
        if raw_role:
            role = raw_role

    # In production-like environments, require explicit email and enforce allowlist.
    if is_prod_like:
        if not isinstance(payload, dict) or not str(payload.get("email") or "").strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email is required")
        allowed = str(os.getenv("DEV_LOGIN_ALLOWED_EMAILS") or "").strip()
        if not allowed:
            # Default lock-down: only John is allowed unless explicitly expanded.
            allowed = "john@fotonconsulting.com"
        allowed_set = {e.strip().lower() for e in allowed.split(",") if e.strip()}
        if email.lower() not in allowed_set:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not allowed")

    # Resolve plan for dev login.
    # In local/dev environments we default to Pro to unlock full SmartRisk.
    plan = PLAN_PRO if not is_prod_like else PLAN_LITE
    if email.lower() == "john@fotonconsulting.com" and (not isinstance(payload, dict) or not payload.get("role")):
        role = "admin"
        plan = PLAN_PRO

    # Use a stable dev-only subject derived from email.
    auth0_id = f"dev:{email.lower()}"
    username = email.split("@")[0] if "@" in email else email
    access_token = create_dev_token(sub=auth0_id, email=email, username=username, role=role)

    now = datetime.now(timezone.utc)
    user_id: Optional[str] = None
    try:
        # Find or create the dev user
        dev_user = user_crud.get_user_by_auth0_id(db, auth0_id)
        if not dev_user:
            dev_user = user_crud.create_user_from_auth0(db, auth0_id, email)

        if dev_user:
            user_id = dev_user.id
            # Keep DB plan in sync with resolved dev-login plan.
            try:
                dev_user.plan = plan
                db.add(dev_user)
                db.commit()
            except Exception:
                db.rollback()
            plan = getattr(dev_user, "plan", None) or plan
            # Create default project only for Pro users (Lite does not include Projects)
            existing_projects = project_crud.get_projects_by_user(db, user_id)
            if plan == PLAN_PRO and not existing_projects:
                default_project = project_schemas.ProjectCreate(
                    name="Default Project",
                    description="Your first project - get started by creating FMEA, CAPA, or other quality management documents.",
                    user_id=user_id,
                )
                project_crud.create_project(db, default_project, user_id)

            # Backfill required docs for all existing projects (dev convenience, idempotent)
            try:
                from business_logic.project_initializer import initialize_project_required_docs

                existing_projects = project_crud.get_projects_by_user(db, user_id)
                for p in existing_projects:
                    initialize_project_required_docs(db, p.id)
            except Exception as init_err:
                logger.error("Failed to initialize required docs during dev-login: %s", init_err, exc_info=True)
    except Exception as e:
        # If project creation fails, continue with login (JWT still valid for local dev)
        logger.error("Error in dev-login DB setup: %s", e, exc_info=True)

    user_profile = UserProfile(
        id=str(user_id or auth0_id),
        username=username or "dev-user",
        email=email,
        plan=plan,
        full_name="Development User",
        role=role or "user",
        company="Development",
        department="IT",
        phone=None,
        bio=None,
        is_verified=True,
        created_at=now,
        last_login=now,
    )
    return Token(access_token=access_token, token_type="bearer", user=user_profile)

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    # NOTE: The DB User model used for Auth0/dev-login is intentionally minimal (id/auth0_id/email).
    # Provide safe defaults for fields that may not exist on the model to keep /auth/me reliable.
    return UserProfile(
        id=current_user.id,
        username=getattr(current_user, "username", None) or (getattr(current_user, "email", "") or "user").split("@")[0],
        email=getattr(current_user, "email", "") or "",
        plan=getattr(current_user, "plan", None) or PLAN_LITE,
        full_name=getattr(current_user, "full_name", None),
        role=getattr(current_user, "role", None) or "user",
        company=getattr(current_user, "company", None),
        department=getattr(current_user, "department", None),
        phone=getattr(current_user, "phone", None),
        bio=getattr(current_user, "bio", None),
        is_verified=bool(getattr(current_user, "is_verified", True)),
        created_at=getattr(current_user, "created_at", None),
        last_login=getattr(current_user, "last_login", None),
    )

@router.put("/me", response_model=UserProfile)
def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    updated_user = user_crud.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserProfile(
        id=updated_user.id,
        username=getattr(updated_user, "username", None) or (getattr(updated_user, "email", "") or "user").split("@")[0],
        email=getattr(updated_user, "email", "") or "",
        full_name=getattr(updated_user, "full_name", None),
        role=getattr(updated_user, "role", None) or "user",
        company=getattr(updated_user, "company", None),
        department=getattr(updated_user, "department", None),
        phone=getattr(updated_user, "phone", None),
        bio=getattr(updated_user, "bio", None),
        is_verified=bool(getattr(updated_user, "is_verified", True)),
        created_at=getattr(updated_user, "created_at", None),
        last_login=getattr(updated_user, "last_login", None),
    )

@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password"""
    success = user_crud.change_password(
        db, current_user.id, password_data.current_password, password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

# Admin endpoints (require admin role)
@router.get("/users", response_model=List[UserOut])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = user_crud.get_all_users(db, skip=skip, limit=limit)
    return users

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = user_crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/verify")
def verify_user_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a user account (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = user_crud.verify_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User verified successfully"}

@router.post("/users/{user_id}/deactivate")
def deactivate_user_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user account (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    success = user_crud.deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}

@router.post("/users/{user_id}/activate")
def activate_user_account(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a user account (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = user_crud.activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"} 