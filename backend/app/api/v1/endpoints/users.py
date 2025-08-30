"""
User management endpoints
"""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_superuser
from app.models.user import User
from app.schemas.user import User as UserSchema, UserProfile, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update current user profile"""
    
    # Update user fields
    update_data = user_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """Get all users (superuser only)"""
    # TODO: Implement user listing with pagination
    return []


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get user by ID"""
    # TODO: Implement user retrieval with proper permissions
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not implemented yet"
    )
