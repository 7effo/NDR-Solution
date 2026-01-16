"""
Case Management Service for MCP
Interacts with the alert-manager service
"""
import httpx
import structlog
from typing import List, Dict, Any, Optional

logger = structlog.get_logger()

ALERT_MANAGER_URL = "http://alert-manager:6000"

async def list_cases(status: str = "open") -> List[Dict[str, Any]]:
    """List cases from alert manager"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{ALERT_MANAGER_URL}/cases", params={"status": status})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("Failed to list cases", error=str(e))
            return []

async def create_case(title: str, description: str, severity: str = "medium") -> Dict[str, Any]:
    """Create a new case"""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "title": title,
                "description": description,
                "severity": severity
            }
            resp = await client.post(f"{ALERT_MANAGER_URL}/cases", json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("Failed to create case", error=str(e))
            return {"error": str(e)}

async def add_comment(case_id: int, content: str, user: str = "AI_Agent") -> Dict[str, Any]:
    """Add a comment to a case"""
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "user": user,
                "content": content
            }
            resp = await client.post(f"{ALERT_MANAGER_URL}/cases/{case_id}/comments", json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error("Failed to add comment", error=str(e))
            return {"error": str(e)}
