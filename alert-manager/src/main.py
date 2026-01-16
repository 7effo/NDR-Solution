"""
Alert Manager Main Service
"""
import asyncio
import structlog
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Body
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from .config import settings
from .correlation import CorrelationEngine
from .database import engine, get_db, SessionLocal
from .models import Base, Case, CaseComment, CaseArtifact, Alert

logger = structlog.get_logger()

correlation_engine = None

# Pydantic Models
class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    assignee: Optional[str] = None

class CommentCreate(BaseModel):
    user: str
    content: str

class CaseResponse(BaseModel):
    id: int
    title: str
    status: str
    severity: str
    created_at: datetime
    assignee: Optional[str]

    class Config:
        from_attributes = True

async def correlation_loop():
    """Background loop for correlation"""
    while True:
        if correlation_engine:
            await correlation_engine.run_correlation_cycle()
        await asyncio.sleep(settings.CORRELATION_INTERVAL_SECONDS)

def create_tables():
    Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting ThunderX Alert Manager")
    
    # Create tables
    create_tables()
    
    global correlation_engine
    correlation_engine = CorrelationEngine()
    
    # Start background correlation
    asyncio.create_task(correlation_loop())
    
    yield
    logger.info("Shutting down ThunderX Alert Manager")

app = FastAPI(
    title="ThunderX Alert Manager",
    description="Alert correlation and case management",
    version=settings.VERSION,
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# --- Case Management API ---

@app.get("/cases", response_model=List[CaseResponse])
def list_cases(status: str = "open", db: Session = Depends(get_db)):
    cases = db.query(Case).filter(Case.status == status).order_by(Case.created_at.desc()).all()
    return cases

@app.post("/cases", response_model=CaseResponse)
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    db_case = Case(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@app.get("/cases/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Manually construction response to include relation counts/details if needed
    # For now returning simple dict to allow flexibility
    return {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "severity": case.severity,
        "assignee": case.assignee,
        "created_at": case.created_at,
        "alerts_count": len(case.alerts),
        "comments": [{"user": c.user, "content": c.content, "timestamp": c.created_at} for c in case.comments]
    }

@app.post("/cases/{case_id}/comments")
def add_comment(case_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db_comment = CaseComment(
        case_id=case_id,
        user=comment.user,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    return {"status": "comment added"}

@app.put("/cases/{case_id}/close")
def close_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = "closed"
    db.commit()
    return {"status": "case closed"}

def main():
    logger.info("Starting Alert Manager", port=settings.PORT)
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()
