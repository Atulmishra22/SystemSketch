"""
Room Model - SQLAlchemy 2.0 with Async Support
Stores room metadata and canvas state
"""
from sqlalchemy import String, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
import uuid

from app.core.database import Base


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
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    last_activity: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )
    
    # Future: creator_id foreign key will be added in Phase 2
    creator_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True
    )
    
    # Future: permission level for access control (Phase 3)
    permission_level: Mapped[str] = mapped_column(
        String(20),
        default="public",
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name={self.name}, is_saved={self.is_saved})>"
