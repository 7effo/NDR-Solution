"""Threat intel routes"""

from fastapi import APIRouter, Depends
from .auth import get_current_user, User

router = APIRouter()

@router.get("/")
async def get_threat_intel(current_user: User = Depends(get_current_user)):
    """Get threat intelligence indicators"""
    # TODO: Implement
    return {"indicators": [], "total": 0}
