"""
ThunderX API Gateway
Main application entry point
"""

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .routes import health, auth, query, alerts, threat_intel, system

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="ThunderX API Gateway",
    description="REST API for ThunderX NDR Platform",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(threat_intel.router, prefix="/threat-intel", tags=["threat-intelligence"])
app.include_router(system.router, prefix="/system", tags=["system"])


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "ThunderX API Gateway",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }


def main():
    """Main entry point"""
    logger.info("Starting ThunderX API Gateway", version=settings.VERSION, port=settings.PORT)
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    main()
