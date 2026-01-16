"""
Threat Intel Service Main Application
"""
import asyncio
import structlog
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, get_db
from .models import Base
from .feed_manager import FeedManager
from .enrichment import router as enrichment_router

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ThunderX Threat Intel Service")
    
    # Initial feed update in background
    # We can't pass DB session easily to background task here without handling scope
    # For now, we'll just start the server. 
    # Real implementations would use a task queue like Celery.
    
    yield
    logger.info("Shutting down ThunderX Threat Intel Service")

app = FastAPI(
    title="ThunderX Threat Intel Service",
    description="Threat intelligence aggregation and management",
    version=settings.VERSION,
    lifespan=lifespan
)

app.include_router(enrichment_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@app.get("/feeds/update")
async def trigger_update(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger feed update"""
    # Note: This is simplified. Passing db session to background task can be tricky if session closes.
    # Ideally, the background task creates its own session.
    background_tasks.add_task(run_feed_update)
    return {"status": "update_started"}

def run_feed_update():
    """Helper to run update with its own session"""
    from .database import SessionLocal
    db = SessionLocal()
    try:
        manager = FeedManager(db)
        # Run async method in sync wrapper if needed, or better:
        # Since FeedManager uses httpx (async), we need an event loop.
        # But this function is run in a thread pool by FastAPI background tasks (def).
        # We need asyncio.run()
        asyncio.run(manager.update_all_feeds())
    finally:
        db.close()

def main():
    logger.info("Starting Threat Intel Service", port=settings.PORT)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()
