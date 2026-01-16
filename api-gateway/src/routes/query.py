"""
Query proxy routes - forwards to MCP AI service
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx

from ..config import settings
from .auth import get_current_user, User

router = APIRouter()


class QueryRequest(BaseModel):
    """Query request"""
    query: str
    index_pattern: Optional[str] = "*"
    size: Optional[int] = 100


@router.post("/")
async def execute_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute natural language query
    
    Proxies to MCP AI service for translation and execution
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.MCP_AI_SERVICE_URL}/query/",
                json=request.dict(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"MCP AI service error: {str(e)}")


@router.get("/examples")
async def get_query_examples(current_user: User = Depends(get_current_user)):
    """Get example queries"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MCP_AI_SERVICE_URL}/query/examples",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"MCP AI service error: {str(e)}")
