"""
Evaluation management endpoints
"""

from typing import Any
from fastapi import APIRouter, Depends
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def read_evaluations(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get evaluations"""
    return {"message": "Evaluations endpoint - not implemented yet"}


@router.post("/")
async def create_evaluation(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Create new evaluation"""
    return {"message": "Create evaluation endpoint - not implemented yet"}


@router.get("/{evaluation_id}")
async def read_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get evaluation by ID"""
    return {"message": f"Evaluation {evaluation_id} endpoint - not implemented yet"}
