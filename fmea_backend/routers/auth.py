from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserOut, UserProfile, Token, UserUpdate, PasswordChange
from crud import user as user_crud
from auth.security import create_access_token, verify_token, get_password_hash, verify_password
from auth.dependencies import get_current_user
from datetime import timedelta

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
def dev_login():
    """Development login endpoint"""
    from auth.security import create_dev_token
    from crud import project as project_crud
    from crud import user as user_crud
    from schemas import project as project_schemas
    from database import get_db
    
    access_token = create_dev_token()
    
    # Get or create dev user and their default project
    db = next(get_db())
    user_id = None
    try:
        # Find or create the dev user
        dev_user = user_crud.get_user_by_auth0_id(db, "dev-user")
        if not dev_user:
            dev_user = user_crud.create_user_from_auth0(db, "dev-user", "dev@example.com")
        
        if dev_user:
            user_id = dev_user.id
            # Create default project if none exist
            existing_projects = project_crud.get_projects_by_user(db, user_id)
            if not existing_projects:
                default_project = project_schemas.ProjectCreate(
                    name="Default Project",
                    description="Your first project - get started by creating FMEA, CAPA, or other quality management documents.",
                    user_id=user_id
                )
                project_crud.create_project(db, default_project, user_id)

            # Backfill required docs for all existing projects (dev convenience, idempotent)
            try:
                from business_logic.project_initializer import initialize_project_required_docs
                existing_projects = project_crud.get_projects_by_user(db, user_id)
                for p in existing_projects:
                    initialize_project_required_docs(db, p.id)
            except Exception as init_err:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to initialize required docs during dev-login: {init_err}", exc_info=True)
    except Exception as e:
        # If project creation fails, continue with login
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in dev-login setup: {str(e)}", exc_info=True)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id or "dev-user",
            "username": "dev-user",
            "email": "dev@example.com",
            "full_name": "Development User",
            "role": "admin",
            "company": "Development",
            "department": "IT",
            "phone": None,
            "bio": None,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T00:00:00Z"
        }
    }

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company=current_user.company,
        department=current_user.department,
        phone=current_user.phone,
        bio=current_user.bio,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
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
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role,
        company=updated_user.company,
        department=updated_user.department,
        phone=updated_user.phone,
        bio=updated_user.bio,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at,
        last_login=updated_user.last_login
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