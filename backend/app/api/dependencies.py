"""
Dependency Injection Functions
Common dependencies for route handlers
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session


# Security scheme for JWT (will be implemented in Phase 2)
security = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> Optional[dict]:
    """
    Get current user from JWT token (optional - returns None if not authenticated)
    This allows endpoints to support both anonymous and authenticated access
    
    Phase 2: Will decode JWT and return user object
    For now: Returns None (anonymous mode)
    """
    if not credentials:
        return None
    
    # Future: Decode JWT token and fetch user
    # from app.services.auth_service import decode_token
    # user_id = decode_token(credentials.credentials)
    # user = await session.get(User, user_id)
    # return user
    
    return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Get current user from JWT token (required - raises 401 if not authenticated)
    
    Phase 2: Will decode JWT and return user object
    For now: Raises exception (auth not implemented yet)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Future: Decode JWT token and fetch user
    # from app.services.auth_service import decode_token
    # try:
    #     user_id = decode_token(credentials.credentials)
    #     user = await session.get(User, user_id)
    #     if not user:
    #         raise HTTPException(status_code=401, detail="User not found")
    #     return user
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail="Invalid token")
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not implemented yet (Phase 2)"
    )
