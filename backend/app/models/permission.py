"""
Permission Enum and RoomPermission Model
Defines permission levels and user-room access control
"""
from sqlalchemy import String, Enum as SQLEnum, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING
import enum
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.room import Room


class PermissionLevel(str, enum.Enum):
    """Permission levels for room access"""
    OWNER = "owner"      # Full control: edit, invite, delete
    EDITOR = "editor"    # Can edit canvas and see all content
    VIEWER = "viewer"    # Read-only access, cannot edit


class RoomPermission(Base):
    """
    Junction table for user-room permissions
    Implements many-to-many relationship with permission levels
    """
    
    __tablename__ = "room_permissions"
    
    # Composite primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    room_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Permission level
    permission: Mapped[PermissionLevel] = mapped_column(
        SQLEnum(PermissionLevel),
        nullable=False,
        default=PermissionLevel.VIEWER
    )
    
    # Timestamps
    granted_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    granted_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="permissions")
    room: Mapped["Room"] = relationship("Room", foreign_keys=[room_id], back_populates="permissions")
    granter: Mapped["User"] = relationship("User", foreign_keys=[granted_by])
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "room_id", name="unique_user_room"),
    )
    
    def __repr__(self) -> str:
        return f"<RoomPermission(user_id={self.user_id}, room_id={self.room_id}, permission={self.permission})>"
