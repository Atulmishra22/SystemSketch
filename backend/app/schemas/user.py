"""
User Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters, underscores, and hyphens"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserResponse(BaseModel):
    """Schema for user response (excludes password)"""
    id: str
    username: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Schema for decoded JWT token data"""
    user_id: str
    username: str
