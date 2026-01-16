"""
ThunderX MCP AI Service
Main application entry point
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routes import mcp, query, health, tools
from .services.opensearch_client import OpenSearchClient
from .services.mcp_client import MCPClient
from .services.threat_hunting import ThreatHuntingService
from .services.incident_response import IncidentResponseService

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting ThunderX MCP AI Service", version=settings.VERSION)
    
    # Initialize clients
    app.state.opensearch_client = OpenSearchClient()
    app.state.mcp_client = MCPClient()
    
    # Initialize services
    app.state.threat_hunting_service = ThreatHuntingService(app.state.opensearch_client)
    app.state.incident_response_service = IncidentResponseService()
    
    # Connect to OpenSearch MCP server
    try:
        await app.state.mcp_client.connect()
        logger.info("Connected to OpenSearch MCP server")
    except Exception as e:
        logger.error("Failed to connect to OpenSearch MCP server", error=str(e))
    
    yield
    
    # Cleanup
    logger.info("Shutting down ThunderX MCP AI Service")
    await app.state.mcp_client.disconnect()


# Create FastAPI app
app = FastAPI(
    title="ThunderX MCP AI Service",
    description="AI-powered network security analysis using MCP",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
app.include_router(tools.router, prefix="/tools", tags=["tools"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ThunderX MCP AI Service",
        "version": settings.VERSION,
        "status": "running"
    }


def main():
    """Main entry point"""
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main()
