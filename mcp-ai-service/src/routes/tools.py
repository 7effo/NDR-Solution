"""
Tools API Router
Exposes internal services as callable tools
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..services import case_management

router = APIRouter()

# --- Models ---

class InvestigateIPRequest(BaseModel):
    ip_address: str
    time_range: Optional[str] = "now-24h"

class RemediationRequest(BaseModel):
    alert_id: str
    alert_context: Dict[str, Any]

class CreateCaseRequest(BaseModel):
    title: str
    description: str
    severity: str = "medium"

class AddCommentRequest(BaseModel):
    content: str
    user: str = "AI_Agent"

# --- Routes ---

@router.post("/investigate_ip")
async def investigate_ip(request: Request, body: InvestigateIPRequest):
    """
    Tool: Investigate IP Address
    """
    try:
        service = request.app.state.threat_hunting_service
        result = await service.investigate_ip(body.ip_address, body.time_range)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_remediation")
async def generate_remediation(request: Request, body: RemediationRequest):
    """
    Tool: Generate Remediation
    """
    try:
        service = request.app.state.incident_response_service
        result = await service.generate_remediation(body.alert_context)
        return {"remediation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cases")
async def list_cases(status: str = "open"):
    """
    Tool: List open security cases
    """
    return await case_management.list_cases(status)

@router.post("/cases")
async def create_case(body: CreateCaseRequest):
    """
    Tool: Create a new security case
    """
    return await case_management.create_case(
        title=body.title,
        description=body.description,
        severity=body.severity
    )

@router.post("/cases/{case_id}/comments")
async def add_case_comment(case_id: int, body: AddCommentRequest):
    """
    Tool: Add a comment to a case
    """
    return await case_management.add_comment(
        case_id=case_id,
        content=body.content,
        user=body.user
    )
