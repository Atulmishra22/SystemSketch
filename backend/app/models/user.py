"""
User Model - SQLAlchemy 2.0 with Async Support
Stores user accounts for room ownership and authentication
"""
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.room import Room
    from app.models.permission import RoomPermission


class User(Base):
    """User model for authentication and room ownership"""
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # User credentials
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
# Relationships — lazy="select" (load only when accessed, not on every
    # User load).  Previously "selectin" caused every auth check to eagerly
    # pull ALL rooms and ALL permissions for the user.
    created_rooms: Mapped[List["Room"]] = relationship(
        "Room",
        back_populates="creator",
        foreign_keys="Room.creator_id",
        lazy="select"
    )

    permissions: Mapped[List["RoomPermission"]] = relationship(
        "RoomPermission",
        back_populates="user",
        foreign_keys="RoomPermission.user_id",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"
