"""
Room REST API Endpoints
Handles room creation, retrieval, and persistence
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_async_session
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse, RoomState, RoomSaveRequest
from app.core.state_manager import room_state_manager


router = APIRouter()


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_data: RoomCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Create a new collaborative room
    Returns room ID and metadata
    """
    # Create new room in database
    new_room = Room(
        name=room_data.name,
        is_saved=False,
        canvas_state={"shapes": []}
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
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get room metadata and current canvas state
    Returns from in-memory if active, else from database
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
    session: AsyncSession = Depends(get_async_session)
):
    """
    Save current room state to database
    Persists the canvas for future access
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
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete a room (cleanup)
    Future: Will check ownership permissions
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
    Future: Will filter by user ownership
    """
    result = await session.execute(
        select(Room)
        .order_by(Room.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rooms = result.scalars().all()
    
    return rooms
