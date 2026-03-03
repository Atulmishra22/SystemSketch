"""
Authentication Service
Handles password hashing, JWT token creation and validation
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
"""
import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.schemas.user import TokenData


def _prehash(password: str) -> bytes:
    """
    SHA-256 hash + base64 encode the password before passing to bcrypt.

    bcrypt silently truncated passwords longer than 72 bytes in older
    versions; newer versions (4.x) raise a ValueError instead. Pre-hashing
    with SHA-256 and base64-encoding is the approach recommended by the
    official pyca/bcrypt documentation to handle arbitrarily long passwords
    safely while keeping the result well within the 72-byte limit.
    """
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Tries the current prehash approach (SHA-256 + base64 → bcrypt) first.
    Falls back to a direct bcrypt check for accounts that were hashed with
    the old passlib-based method (plain UTF-8 bytes → bcrypt) so that
    existing users are not locked out after the migration.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Hashed password from database

    Returns:
        True if passwords match, False otherwise
    """
    hashed = hashed_password.encode("utf-8")
    # New method: prehash with SHA-256 + base64
    if bcrypt.checkpw(_prehash(plain_password), hashed):
        return True
    # Legacy fallback: passlib stored bcrypt(raw_utf8_bytes)
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived JWT refresh token (7 days by default).
    Carries a ``type: "refresh"`` claim so it cannot be used in place of
    an access token by accident.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT access token.
    Rejects tokens that carry a ``type`` claim other than ``"access"`` so
    that refresh tokens cannot be used as access tokens.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Reject refresh tokens being passed as access tokens.
        # Tokens minted before the type claim was added have type=None,
        # which we treat as "access" for backwards compatibility.
        token_type = payload.get("type")
        if token_type is not None and token_type != "access":
            return None

        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None:
            return None
        
        return TokenData(user_id=user_id, username=username)
    
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT refresh token.
    Only accepts tokens that carry ``type: "refresh"``.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        user_id: str = payload.get("sub")
        username: str = payload.get("username")

        if user_id is None:
            return None

        return TokenData(user_id=user_id, username=username)

    except JWTError:
        return None
