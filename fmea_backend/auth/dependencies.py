from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, PLAN_LITE, PLAN_PRO
from crud import user as user_crud
from auth.security import verify_token
import os

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
    
    # Attach ephemeral identity/role fields from the token payload (no schema change required).
    # This ensures /auth/me can reflect roles for dev tokens and keeps frontend auth consistent.
    token_email = (payload.get("email") or "") or getattr(user, "email", "") or ""
    token_username = payload.get("username") or (token_email.split("@")[0] if "@" in token_email else None)
    token_role = payload.get("role") or "user"

    env = (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or os.getenv("ENV") or "development").lower()

    # Special-case: John has admin access and Pro plan
    if str(token_email).lower() == "john@fotonconsulting.com":
        token_role = "admin"
        try:
            setattr(user, "plan", PLAN_PRO)
        except Exception:
            pass
    # In local/dev, all dev identities get Pro for full SmartRisk UX.
    if str(auth0_id).startswith("dev:") and env not in ("production", "prod", "staging"):
        try:
            setattr(user, "plan", PLAN_PRO)
        except Exception:
            pass

    # Production allowlist: only allow specific users (default: John).
    if env in ("production", "prod", "staging"):
        allowed = str(os.getenv("DEV_LOGIN_ALLOWED_EMAILS") or "").strip() or "john@fotonconsulting.com"
        allowed_set = {e.strip().lower() for e in allowed.split(",") if e.strip()}
        if token_email.lower() not in allowed_set:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not allowed")

    try:
        setattr(user, "email", token_email or getattr(user, "email", ""))
    except Exception:
        pass
    try:
        setattr(user, "username", token_username)
    except Exception:
        pass
    try:
        setattr(user, "role", token_role)
    except Exception:
        pass

    # Ensure plan is set (from DB, John override, or default)
    if not getattr(user, "plan", None) or str(getattr(user, "plan", "")).strip() == "":
        try:
            setattr(user, "plan", PLAN_LITE)
        except Exception:
            pass

    # Local development: default to SmartRisk Pro for every authenticated user (Auth0 + dev tokens).
    # Opt out with SMARTRISK_DEV_FORCE_PRO=false (or 0/no/off). Ignored in production/staging.
    if env not in ("production", "prod", "staging"):
        raw = os.getenv("SMARTRISK_DEV_FORCE_PRO", "true").strip().lower()
        if raw not in ("0", "false", "no", "off"):
            try:
                setattr(user, "plan", PLAN_PRO)
            except Exception:
                pass

    return user
