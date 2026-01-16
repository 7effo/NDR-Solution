"""System routes"""

from fastapi import APIRouter, Depends
from .auth import get_current_user, User

router = APIRouter()

@router.get("/status")
async def get_system_status(current_user: User = Depends(get_current_user)):
    """Get system status"""
    # TODO: Implement real status checks
    return {
        "components": {
            "opensearch": "unknown",
            "zeek": "unknown",
            "suricata": "unknown",
            "arkime": "unknown",
            "mcp_ai": "unknown"
        }
    }
