"""
Dependency Injection Functions
Common dependencies for route handlers with JWT authentication
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.user import User
from app.services.auth_service import decode_access_token


# Security scheme for JWT
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> Optional[User]:
    """
    Get current user from JWT token (optional - returns None if not authenticated)
    This allows endpoints to support both anonymous and authenticated access
    
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    # Decode JWT token
    token_data = decode_access_token(credentials.credentials)
    
    if not token_data:
        return None
    
    # Fetch user from database
    user = await session.get(User, token_data.user_id)
    
    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Get current user from JWT token (required - raises 401 if not authenticated)
    
    Returns:
        User object
    
    Raises:
        HTTPException: 401 if not authenticated or invalid token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode JWT token
    token_data = decode_access_token(credentials.credentials)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await session.get(User, token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
