"""
FastAPI routes for natural language query endpoint
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import structlog

from ..services.query_translator import QueryTranslator
from ..services.opensearch_client import OpenSearchClient

logger = structlog.get_logger()
router = APIRouter()


class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str
    index_pattern: Optional[str] = "*"
    size: Optional[int] = 100


class QueryResponse(BaseModel):
    """Query response"""
    query: str
    opensearch_query: dict
    results: list
    total: int
    took_ms: int
    explanation: Optional[str] = None


@router.post("/", response_model=QueryResponse)
async def execute_natural_language_query(request_body: QueryRequest, request: Request):
    """
    Execute a natural language query against OpenSearch
    
    Example queries:
    - "Show me all suspicious DNS queries in the last 24 hours"
    - "What are the top 10 source IPs by traffic volume?"
    - "Find connections to known malicious IPs"
    - "Show failed SSH login attempts"
    """
    try:
        logger.info("Received natural language query", query=request_body.query)
        
        # Get services from app state
        opensearch_client: OpenSearchClient = request.app.state.opensearch_client
        
        # Translate natural language to OpenSearch DSL
        translator = QueryTranslator()
        opensearch_query = await translator.translate(
            request_body.query,
            request_body.index_pattern
        )
        
        # Override size if provided
        if request_body.size:
            opensearch_query["size"] = request_body.size
        
        # Execute query
        results = await opensearch_client.search(
            index=request_body.index_pattern,
            body=opensearch_query
        )
        
        # Extract hits
        hits = results.get("hits", {}).get("hits", [])
        total = results.get("hits", {}).get("total", {}).get("value", 0)
        took_ms = results.get("took", 0)
        
        return QueryResponse(
            query=request_body.query,
            opensearch_query=opensearch_query,
            results=[hit["_source"] for hit in hits],
            total=total,
            took_ms=took_ms,
            explanation=opensearch_query.get("explanation")
        )
        
    except Exception as e:
        logger.error("Query execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples")
async def get_example_queries():
    """Get example queries users can try"""
    return {
        "examples": [
            {
                "category": "Network Traffic",
                "queries": [
                    "Show me top talkers in the last hour",
                    "What are the most common destination ports?",
                    "Show me all connections to external IPs",
                    "Find large data transfers over 1GB"
                ]
            },
            {
                "category": "Security Alerts",
                "queries": [
                    "Show me all critical alerts in the last 24 hours",
                    "What are the most frequent alert signatures?",
                    "Find alerts related to malware",
                    "Show me suspicious DNS queries"
                ]
            },
            {
                "category": "Threat Hunting",
                "queries": [
                    "Find connections to known malicious IPs",
                    "Show me beaconing behavior",
                    "Detect port scanning activity",
                    "Find unusual authentication attempts"
                ]
            },
            {
                "category": "Protocol Analysis",
                "queries": [
                    "Show me all HTTP traffic",
                    "Find SSL/TLS connections with weak ciphers",
                    "Show DNS queries to newly observed domains",
                    "Find SMB connections"
                ]
            }
        ]
    }
