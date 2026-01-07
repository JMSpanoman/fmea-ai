from jose import jwt, JWTError
from jose.utils import base64url_decode
import requests
from typing import Optional, Dict
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "")
AUTH0_ALGORITHMS = ["RS256"]

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
    try:
        if not AUTH0_DOMAIN:
            # Fallback to simple JWT validation if Auth0 not configured
            from jose import jwt as jose_jwt
            SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
            try:
                payload = jose_jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                return payload
            except JWTError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"JWT decode error (fallback): {str(e)}")
                return None
        
        # Get signing key from JWKS
        signing_key = get_signing_key(token)
        if not signing_key:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Failed to get signing key from JWKS")
            return None
        
        # Verify token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except JWTError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"JWT verification error: {str(e)}")
        return None
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Token verification error: {str(e)}", exc_info=True)
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

def create_dev_token() -> str:
    """Create a development token for testing"""
    data = {
        "sub": "dev-user",
        "username": "dev-user",
        "role": "admin",
        "email": "dev@example.com"
    }
    return create_access_token(data, expires_delta=timedelta(days=365))
