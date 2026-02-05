from jose import jwt, JWTError
from jose.utils import base64url_decode
import requests
from typing import Optional, Dict
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables from `.env` only in non-production environments.
if os.getenv("ENVIRONMENT", "").lower() not in ("production", "prod"):
    load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-dsf588bqn08hhddj.us.auth0.com")
API_AUDIENCE = os.getenv("API_AUDIENCE", os.getenv("AUTH0_AUDIENCE", ""))
AUTH0_AUDIENCE = API_AUDIENCE  # Backward compatibility
AUTH0_ALGORITHMS = ["RS256"]
ISSUER = f"https://{AUTH0_DOMAIN}/" if AUTH0_DOMAIN else None

# Cache for JWKS
_jwks_cache = None

def get_jwks() -> Dict:
    """Fetch JWKS from Auth0"""
    global _jwks_cache
    if _jwks_cache is None:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        try:
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch JWKS: {e}")
    return _jwks_cache

def get_signing_key(token: str) -> Optional[str]:
    """Get the signing key for a JWT token from JWKS"""
    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = get_jwks()
        
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header.get("kid"):
                # Construct the public key
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.backends import default_backend
                from cryptography.hazmat.primitives import serialization
                import base64
                
                n = base64url_decode(key["n"].encode("utf-8"))
                e = base64url_decode(key["e"].encode("utf-8"))
                
                public_key = rsa.RSAPublicNumbers(
                    int.from_bytes(e, "big"),
                    int.from_bytes(n, "big")
                ).public_key(default_backend())
                
                pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                return pem
        return None
    except Exception as e:
        raise Exception(f"Failed to get signing key: {e}")

def verify_auth0_token(token: str) -> Optional[Dict]:
    """Verify an Auth0 JWT token"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # If this is a local/dev HS256 token (e.g. /auth/dev-login), validate via SECRET_KEY
        try:
            header = jwt.get_unverified_header(token)
            if header.get("alg") == "HS256":
                from jose import jwt as jose_jwt
                SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
                payload = jose_jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                logger.info("[auth] Token verified using local HS256 (dev) method")
                return payload
        except Exception as header_err:
            logger.debug(f"[auth] Could not inspect token header: {header_err}")

        if not AUTH0_DOMAIN:
            # Fallback to simple JWT validation if Auth0 not configured
            from jose import jwt as jose_jwt
            SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
            try:
                payload = jose_jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                logger.info("[auth] Token verified using fallback JWT method")
                return payload
            except JWTError as e:
                logger.warning(f"[auth] JWT decode error (fallback): {str(e)}")
                return None
        
        # Debug: Decode token without verification to inspect claims
        try:
            unverified_payload = jwt.get_unverified_claims(token)
            token_iss = unverified_payload.get("iss", "N/A")
            token_aud = unverified_payload.get("aud", "N/A")
            logger.info(f"[auth] Token claims - iss: {token_iss}, aud: {token_aud}")
            logger.info(f"[auth] Expected - issuer: {ISSUER}, audience: {AUTH0_AUDIENCE}")
            
            # Check for mismatches
            if ISSUER and token_iss != ISSUER:
                logger.warning(f"[auth] ISSUER mismatch! Token has: {token_iss}, expected: {ISSUER}")
            if AUTH0_AUDIENCE and token_aud != AUTH0_AUDIENCE:
                logger.warning(f"[auth] AUDIENCE mismatch! Token has: {token_aud}, expected: {AUTH0_AUDIENCE}")
        except Exception as decode_error:
            logger.warning(f"[auth] Could not decode token for inspection: {decode_error}")
        
        # Get signing key from JWKS
        signing_key = get_signing_key(token)
        if not signing_key:
            logger.warning("[auth] Failed to get signing key from JWKS")
            return None
        
        # Verify token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE if AUTH0_AUDIENCE else None,
            issuer=ISSUER
        )
        logger.info("[auth] Token verified successfully")
        return payload
    except JWTError as e:
        logger.warning(f"[auth] JWT verification error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"[auth] Token verification error: {str(e)}", exc_info=True)
        return None

def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token (Auth0 or fallback)"""
    return verify_auth0_token(token)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_dev_token(
    *,
    sub: str = "dev-user",
    email: str = "dev@example.com",
    username: str = "dev-user",
    role: str = "admin",
) -> str:
    """Create a development token for testing (HS256)."""
    data = {
        "sub": sub,
        "username": username,
        "role": role,
        "email": email,
    }
    return create_access_token(data, expires_delta=timedelta(days=365))
