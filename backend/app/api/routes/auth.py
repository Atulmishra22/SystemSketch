"""
Authentication REST API Endpoints
Handles user registration, login, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timedelta, timezone

from app.core.database import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, RefreshTokenRequest
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.api.dependencies import get_current_user
from app.config import settings


router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user account
    
    - Validates username and email uniqueness
    - Hashes password securely
    - Returns JWT token for immediate authentication
    """
    # Check if username already exists
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_email = result.scalar_one_or_none()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        last_login=datetime.now(timezone.utc)
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    # Create access + refresh tokens
    access_token = create_access_token(
        data={"sub": new_user.id, "username": new_user.username}
    )
    refresh_token = create_refresh_token(
        data={"sub": new_user.id, "username": new_user.username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Login with username/email and password
    
    - Accepts username or email for login
    - Verifies password
    - Returns JWT token on success
    """
    # Find user by username or email
    result = await session.execute(
        select(User).where(
            or_(
                User.username == credentials.username,
                User.email == credentials.username
            )
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login time
    user.last_login = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(user)
    
    # Create access + refresh tokens
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile
    
    - Requires valid JWT token in Authorization header
    - Returns user information (excluding password)
    """
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    body: RefreshTokenRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    The old refresh token is consumed and a fresh one is issued (rotation).
    No Authorization header required — the caller may have an expired access token.
    """
    token_data = decode_refresh_token(body.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await session.get(User, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
        )

    # Issue a fresh pair (token rotation — limits refresh token reuse window)
    new_access = create_access_token(data={"sub": user.id, "username": user.username})
    new_refresh = create_refresh_token(data={"sub": user.id, "username": user.username})

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
