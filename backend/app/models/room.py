"""
Room Model - SQLAlchemy 2.0 with Async Support
Stores room metadata and canvas state
"""
from sqlalchemy import String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, List
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.permission import RoomPermission


class Room(Base):
    """Room model for collaborative whiteboard sessions"""
    
    __tablename__ = "rooms"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Room metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Canvas state stored as JSON array of shapes
    canvas_state: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        default=dict
    )
    
    # Persistence flag
    is_saved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Visibility: True = anyone can discover & view; False = invite-only (owner + explicit permissions only)
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    last_activity: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # Room ownership - Foreign key to User (nullable for anonymous rooms)
    creator_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Permission level for access control (Phase 3)
    permission_level: Mapped[str] = mapped_column(
        String(20),
        default="public",
        nullable=False
    )
    
    # Relationships
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_rooms",
        foreign_keys=[creator_id],
        lazy="selectin"
    )
    
    permissions: Mapped[List["RoomPermission"]] = relationship(
        "RoomPermission",
        back_populates="room",
        foreign_keys="RoomPermission.room_id",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name={self.name}, is_saved={self.is_saved})>"
