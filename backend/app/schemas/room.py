"""
Room Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List


class RoomCreate(BaseModel):
    """Schema for creating a new room"""
    name: str = Field(..., min_length=1, max_length=255, description="Room name")


class RoomResponse(BaseModel):
    """Schema for room response"""
    id: str
    name: str
    is_saved: bool
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


class RoomListResponse(BaseModel):
    """Schema for listing multiple rooms"""
    rooms: List[RoomResponse]
    total: int
