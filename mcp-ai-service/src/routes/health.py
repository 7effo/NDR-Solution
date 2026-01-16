"""
Health check endpoint
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    opensearch_connected: bool
    mcp_connected: bool


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request):
    """Health check endpoint"""
    from ..config import settings
    
    # Check OpenSearch connection
    opensearch_connected = False
    try:
        opensearch_client = request.app.state.opensearch_client
        opensearch_connected = await opensearch_client.ping()
    except:
        pass
    
    # Check MCP connection
    mcp_connected = False
    try:
        mcp_client = request.app.state.mcp_client
        mcp_connected = mcp_client.is_connected()
    except:
        pass
    
    return HealthResponse(
        status="healthy" if (opensearch_connected or mcp_connected) else "degraded",
        version=settings.VERSION,
        opensearch_connected=opensearch_connected,
        mcp_connected=mcp_connected
    )
