from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from crud import user as user_crud
from auth.security import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Handle dev user case
    if user_id == "dev-user-123":
        # Return a mock user for development
        class DevUser:
            id = 123
            username = "dev-user"
            email = "dev@example.com"
            full_name = "Development User"
            role = "admin"
            company = "Development"
            department = "IT"
            phone = None
            bio = None
            is_active = True
            is_verified = True
            created_at = "2024-01-01T00:00:00Z"
            last_login = "2024-01-01T00:00:00Z"
        
        return DevUser()
    
    # Get real user from database
    user = user_crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    from auth.security import verify_token as verify_jwt_token
    return verify_jwt_token(token)

def create_dev_token() -> str:
    """Create development token for testing"""
    from auth.security import create_dev_token
    return create_dev_token()
