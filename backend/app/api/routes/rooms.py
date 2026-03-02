"""
Room REST API Endpoints
Handles room creation, retrieval, and persistence with permission checks
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.core.database import get_async_session
from app.models.room import Room
from app.models.user import User
from app.models.permission import PermissionLevel
from app.schemas.room import RoomCreate, RoomResponse, RoomState, RoomSaveRequest
from app.core.state_manager import room_state_manager
from app.api.dependencies import get_current_user_optional, get_current_user
from app.services.permission_service import PermissionService


router = APIRouter()


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Create a new collaborative room
    
    - If authenticated: Room is owned by the user
    - If anonymous: Room has no owner (creator_id is NULL)
    
    Returns room ID and metadata
    """
    # Create new room in database
    new_room = Room(
        name=room_data.name,
        is_saved=False,
        canvas_state={"shapes": []},
        creator_id=current_user.id if current_user else None
    )
    
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    
    # Initialize in-memory state
    await room_state_manager.set_state(new_room.id, [])
    
    return new_room


@router.get("/rooms/{room_id}", response_model=RoomState)
async def get_room(
    room_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get room metadata and current canvas state
    
    - Public rooms: accessible to everyone
    - Private rooms: requires explicit permission
    - Returns from in-memory if active, else from database
    """
    # Try to get from database first
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room {room_id} not found"
        )
    
    # Check permissions
    if current_user:
        # Authenticated user - check explicit permissions
        has_access = await PermissionService.check_permission(
            db=session,
            user_id=current_user.id,
            room_id=room_id,
            required_permission=PermissionLevel.VIEWER
        )
    else:
        # Anonymous user - only public rooms
        has_access = room.permission_level == "public"
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this room"
        )
    
    # Get current state from memory (or use database state if not in memory)
    shapes = await room_state_manager.get_state(room_id)
    
    # If no in-memory state and room is saved, load from database
    if not shapes and room.is_saved and room.canvas_state:
        shapes = room.canvas_state.get("shapes", [])
        await room_state_manager.set_state(room_id, shapes)
    
    return RoomState(
        id=room.id,
        name=room.name,
        shapes=shapes
    )


@router.put("/rooms/{room_id}/save", response_model=RoomResponse)
async def save_room(
    room_id: str,
    save_data: RoomSaveRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Save current room state to database
    
    - Requires EDITOR or OWNER permission
    - Persists the canvas for future access
    """
    # Get room from database
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room {room_id} not found"
        )
    
    # Check permissions - need EDITOR or OWNER
    if current_user:
        has_edit_access = await PermissionService.check_permission(
            db=session,
            user_id=current_user.id,
            room_id=room_id,
            required_permission=PermissionLevel.EDITOR
        )
    else:
        # Anonymous users can save public rooms for now
        has_edit_access = room.permission_level == "public"
    
    if not has_edit_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to save this room (requires editor access)"
        )
    
    # Update room with current state
    room.canvas_state = {"shapes": save_data.shapes}
    room.is_saved = True
    
    await session.commit()
    await session.refresh(room)
    
    # Also update in-memory state
    await room_state_manager.set_state(room_id, save_data.shapes)
    
    return room


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a room
    
    - Requires OWNER permission (room creator or granted owner permission)
    - Requires authentication
    """
    result = await session.execute(
        select(Room).where(Room.id == room_id)
    )
    room = result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room {room_id} not found"
        )
    
    # Check if user is owner
    user_permission = await PermissionService.get_user_permission(
        db=session,
        user_id=current_user.id,
        room_id=room_id
    )
    
    is_owner = (room.creator_id == current_user.id) or (user_permission == PermissionLevel.OWNER)
    
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only room owners can delete rooms"
        )
    
    # Delete from database
    await session.delete(room)
    await session.commit()
    
    # Clean up in-memory state
    await room_state_manager.delete_room(room_id)
    
    return None


@router.get("/rooms", response_model=List[RoomResponse])
async def list_rooms(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_session)
):
    """
    List all rooms (most recent first)
    Returns public rooms and anonymous rooms
    """
    result = await session.execute(
        select(Room)
        .order_by(Room.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rooms = result.scalars().all()
    
    return rooms


@router.get("/users/me/rooms", response_model=List[RoomResponse])
async def list_my_rooms(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    List all rooms accessible by the current authenticated user
    
    - Requires authentication
    - Returns rooms created by the user
    - Returns rooms where user has explicit permissions
    """
    # Get all accessible rooms (owned + shared)
    accessible_rooms = await PermissionService.get_user_accessible_rooms(
        db=session,
        user_id=current_user.id
    )
    
    # Sort by created_at descending
    accessible_rooms.sort(key=lambda r: r.created_at, reverse=True)
    
    # Apply pagination
    paginated_rooms = accessible_rooms[offset:offset + limit]
    
    return paginated_rooms
