"""
User Model - SQLAlchemy 2.0 with Async Support
Stores user accounts for room ownership and authentication
"""
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
import uuid

from app.core.database import Base


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
        default=datetime.utcnow,
        nullable=False
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # Relationships - will be used when Room model is updated
    # rooms: Mapped[List["Room"]] = relationship(
    #     "Room",
    #     back_populates="creator",
    #     cascade="all, delete-orphan"
    # )
    
    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"
