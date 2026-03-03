"""
Room Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List

from app.models.permission import PermissionLevel


class RoomCreate(BaseModel):
    """Schema for creating a new room"""
    name: str = Field(..., min_length=1, max_length=255, description="Room name")
    is_public: bool = Field(default=True, description="True = discoverable by anyone; False = private (invite-only)")


class RoomResponse(BaseModel):
    """Schema for room response"""
    id: str
    name: str
    is_saved: bool
    is_public: bool = True
    created_at: datetime
    last_activity: datetime
    creator_id: Optional[str] = None
    permission_level: str = "public"
    
    model_config = {
        "from_attributes": True  # Pydantic V2: replaces orm_mode = True
    }


class RoomState(BaseModel):
    """Schema for room canvas state"""
    id: str
    name: str
    shapes: List[Dict] = Field(default_factory=list, description="Array of shape objects")
    
    model_config = {
        "from_attributes": True
    }


class RoomSaveRequest(BaseModel):
    """Schema for saving room state"""
    shapes: List[Dict] = Field(..., description="Array of shapes to save")


class RoomUpdate(BaseModel):
    """Schema for renaming/updating a room"""
    name: str = Field(..., min_length=1, max_length=255, description="New room name")


class RoomVisibilityUpdate(BaseModel):
    """Schema for toggling room public/private visibility"""
    is_public: bool = Field(..., description="True = public, False = private")


class RoomListResponse(BaseModel):
    """Schema for listing multiple rooms"""
    rooms: List[RoomResponse]
    total: int


class RoomWithPermission(RoomResponse):
    """Schema for room response with user's permission level"""
    user_permission: Optional[PermissionLevel] = None
    is_owner: bool = False

