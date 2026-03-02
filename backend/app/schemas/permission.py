"""
Permission Schemas - Pydantic V2
Request/Response schemas for room permission management
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from app.models.permission import PermissionLevel


class PermissionBase(BaseModel):
    """Base schema for permission data"""
    permission: PermissionLevel = Field(
        default=PermissionLevel.VIEWER,
        description="Permission level for room access"
    )


class PermissionGrant(PermissionBase):
    """Schema for granting/updating permissions"""
    user_id: str = Field(
        ...,
        description="User ID to grant permission to",
        min_length=36,
        max_length=36
    )
    room_id: str = Field(
        ...,
        description="Room ID to grant permission for",
        min_length=36,
        max_length=36
    )


class PermissionInvite(BaseModel):
    """Schema for inviting users by username/email"""
    username_or_email: str = Field(
        ...,
        description="Username or email of user to invite",
        min_length=3,
        max_length=255
    )
    permission: PermissionLevel = Field(
        default=PermissionLevel.VIEWER,
        description="Permission level to grant"
    )


class PermissionUpdate(BaseModel):
    """Schema for updating existing permission"""
    permission: PermissionLevel = Field(
        ...,
        description="New permission level"
    )


class PermissionResponse(PermissionBase):
    """Schema for permission response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    room_id: str
    granted_at: datetime
    granted_by: Optional[str] = None


class UserPermissionInfo(BaseModel):
    """User information in permission context"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    email: str


class RoomPermissionDetail(PermissionResponse):
    """Detailed permission response with user info"""
    user: UserPermissionInfo
    

class PermissionCheck(BaseModel):
    """Schema for permission check response"""
    has_access: bool
    permission: Optional[PermissionLevel] = None
    is_owner: bool = False
