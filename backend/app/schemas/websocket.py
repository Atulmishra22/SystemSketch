"""
WebSocket Message Schemas for Real-time Communication
"""
from pydantic import BaseModel, Field
from typing import Literal, Union, Dict, Any, Optional


class CursorPosition(BaseModel):
    """Cursor position update"""
    action: Literal["cursor"] = "cursor"
    userId: str
    username: str = "Anonymous"
    color: str
    x: float
    y: float


class DrawShape(BaseModel):
    """Draw a new shape"""
    action: Literal["draw"] = "draw"
    shape: Dict[str, Any]  # Will be validated as Shape union on server


class ClearCanvas(BaseModel):
    """Clear entire canvas"""
    action: Literal["clear"] = "clear"


class UndoAction(BaseModel):
    """Undo last action"""
    action: Literal["undo"] = "undo"


class RedoAction(BaseModel):
    """Redo last undone action"""
    action: Literal["redo"] = "redo"


class UserJoined(BaseModel):
    """Notification when user joins room"""
    action: Literal["user_joined"] = "user_joined"
    userId: str
    username: str
    color: str
    canEdit: bool = False


class UserLeft(BaseModel):
    """Notification when user leaves room"""
    action: Literal["user_left"] = "user_left"
    userId: str


class RoomUsers(BaseModel):
    """Full list of connected users sent to a newly joined user"""
    action: Literal["room_users"] = "room_users"
    users: list[Dict[str, Any]]  # [{userId, username, color, canEdit}]
    myUserId: str
    myColor: str
    myUsername: str
    canEdit: bool


class SyncState(BaseModel):
    """Full canvas state synchronization"""
    action: Literal["sync_state"] = "sync_state"
    shapes: list[Dict[str, Any]]


class ErrorMessage(BaseModel):
    """Error notification"""
    action: Literal["error"] = "error"
    message: str
    code: Optional[str] = None


# Union of all WebSocket message types (incoming)
WSMessageIn = Union[
    CursorPosition,
    DrawShape,
    ClearCanvas,
    UndoAction,
    RedoAction
]

# Union of all WebSocket message types (outgoing)
WSMessageOut = Union[
    CursorPosition,
    DrawShape,
    ClearCanvas,
    UndoAction,
    RedoAction,
    UserJoined,
    UserLeft,
    SyncState,
    ErrorMessage
]
