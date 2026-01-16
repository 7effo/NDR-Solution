"""
MCP-specific routes
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()
router = APIRouter()


class MCPStatusResponse(BaseModel):
    """MCP server status"""
    connected: bool
    server_url: str
    capabilities: dict


@router.get("/status", response_model=MCPStatusResponse)
async def get_mcp_status(request: Request):
    """Get MCP server connection status"""
    try:
        mcp_client = request.app.state.mcp_client
        
        return MCPStatusResponse(
            connected=mcp_client.is_connected(),
            server_url=mcp_client.get_server_url(),
            capabilities=mcp_client.get_capabilities()
        )
    except Exception as e:
        logger.error("Failed to get MCP status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reconnect")
async def reconnect_mcp(request: Request):
    """Reconnect to MCP server"""
    try:
        mcp_client = request.app.state.mcp_client
        await mcp_client.disconnect()
        await mcp_client.connect()
        
        return {"status": "reconnected", "connected": mcp_client.is_connected()}
    except Exception as e:
        logger.error("Failed to reconnect to MCP", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
