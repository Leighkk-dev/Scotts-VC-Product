"""
User schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserInDB(UserBase):
    """User in database schema"""
    id: uuid.UUID
    password_hash: str
    is_verified: bool
    is_superuser: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserBase):
    """User public schema"""
    id: uuid.UUID
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(User):
    """Extended user profile schema"""
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str
    language: str
    preferences: Dict[str, Any]
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
