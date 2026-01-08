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
    """Get current user from Auth0 JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        logger.warning("[auth] Token validation failed - returning 401")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract Auth0 user ID (sub claim)
    auth0_id = payload.get("sub")
    if auth0_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - missing sub claim",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get or create user from database
    user = user_crud.get_user_by_auth0_id(db, auth0_id)
    if user is None:
        # Create user if doesn't exist
        email = payload.get("email", "") or payload.get("email_verified", "") or ""
        user = user_crud.create_user_from_auth0(db, auth0_id, email)
        if user is None:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create user for auth0_id: {auth0_id}, email: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user in database",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return user
