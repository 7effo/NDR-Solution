"""
Enrichment Service API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import IOC

router = APIRouter()

@router.get("/enrich/ip/{ip}")
def enrich_ip(ip: str, db: Session = Depends(get_db)):
    """Check if an IP is in the Threat Intel DB"""
    ioc = db.query(IOC).filter(IOC.value == ip, IOC.type == "ip").first()
    if ioc:
        return {
            "is_malicious": True,
            "confidence": ioc.confidence,
            "source": ioc.source,
            "tags": ioc.tags,
            "last_seen": ioc.last_seen
        }
    return {"is_malicious": False}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get IOC statistics"""
    total = db.query(IOC).count()
    return {"total_iocs": total}
