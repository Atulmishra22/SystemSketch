"""
Permission Management API Routes
Endpoints for managing room access control
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from app.core.database import get_async_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.permission import RoomPermission, PermissionLevel
from app.schemas.permission import (
    PermissionInvite,
    PermissionUpdate,
    PermissionResponse,
    RoomPermissionDetail,
    PermissionCheck,
    UserPermissionInfo
)
from app.services.permission_service import PermissionService


router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/rooms/{room_id}/invite", response_model=RoomPermissionDetail, status_code=status.HTTP_201_CREATED)
async def invite_user_to_room(
    room_id: str,
    invite: PermissionInvite,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Invite a user to a room by username or email
    Only room owners can invite users
    """
    # Find user by username or email
    stmt = select(User).where(
        (User.username == invite.username_or_email) | 
        (User.email == invite.username_or_email)
    )
    result = await db.execute(stmt)
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{invite.username_or_email}' not found"
        )
    
    # Grant permission
    permission = await PermissionService.grant_permission(
        db=db,
        granter_id=current_user.id,
        user_id=target_user.id,
        room_id=room_id,
        permission=invite.permission
    )
    
    # Refresh to get relationships
    await db.refresh(permission, ["user"])
    
    return permission


@router.get("/rooms/{room_id}", response_model=List[RoomPermissionDetail])
async def list_room_permissions(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    List all users with access to a room
    Only accessible by room owner
    """
    permissions = await PermissionService.list_room_permissions(
        db=db,
        room_id=room_id,
        requester_id=current_user.id
    )
    
    # Refresh to get user relationships
    for perm in permissions:
        await db.refresh(perm, ["user"])
    
    return permissions


@router.put("/rooms/{room_id}/users/{user_id}", response_model=PermissionResponse)
async def update_user_permission(
    room_id: str,
    user_id: str,
    update: PermissionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update a user's permission level for a room
    Only room owners can update permissions
    """
    permission = await PermissionService.grant_permission(
        db=db,
        granter_id=current_user.id,
        user_id=user_id,
        room_id=room_id,
        permission=update.permission
    )
    
    return permission


@router.delete("/rooms/{room_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_user_permission(
    room_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Revoke a user's access to a room
    Only room owners can revoke permissions
    """
    revoked = await PermissionService.revoke_permission(
        db=db,
        revoker_id=current_user.id,
        user_id=user_id,
        room_id=room_id
    )
    
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return None


@router.get("/rooms/{room_id}/check", response_model=PermissionCheck)
async def check_room_access(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Check current user's access level for a room
    """
    permission = await PermissionService.get_user_permission(
        db=db,
        user_id=current_user.id,
        room_id=room_id
    )
    
    # Check if user is owner
    from app.models.room import Room
    room = await db.get(Room, room_id)
    is_owner = room.creator_id == current_user.id if room else False
    
    return PermissionCheck(
        has_access=permission is not None,
        permission=permission,
        is_owner=is_owner
    )


@router.get("/users/{user_id}/rooms/{room_id}", response_model=PermissionResponse)
async def get_user_room_permission(
    user_id: str,
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get a specific user's permission for a room
    Only accessible by room owner or the user themselves
    """
    # Check if requester is the user or room owner
    if current_user.id != user_id:
        from app.models.room import Room
        room = await db.get(Room, room_id)
        if not room or room.creator_id != current_user.id:
            requester_perm = await PermissionService.get_user_permission(
                db, current_user.id, room_id
            )
            if requester_perm != PermissionLevel.OWNER:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this permission"
                )
    
    # Get permission
    stmt = select(RoomPermission).where(
        and_(
            RoomPermission.user_id == user_id,
            RoomPermission.room_id == room_id
        )
    )
    result = await db.execute(stmt)
    permission = result.scalar_one_or_none()
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return permission
