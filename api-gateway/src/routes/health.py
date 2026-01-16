"""
Health check endpoint
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health response model"""
    status: str
    version: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from ..config import settings
    
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # TODO: Check database, OpenSearch, etc.
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive"}
