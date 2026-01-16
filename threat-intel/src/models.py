"""
Database models for Threat Intelligence
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class IOC(Base):
    """
    Indicator of Compromise
    """
    __tablename__ = "iocs"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, unique=True, index=True, nullable=False) # IP, Domain, Hash
    type = Column(String, index=True, nullable=False) # ip, domain, md5, sha256
    source = Column(String, nullable=False) # threatfox, abuseipdb, etc.
    confidence = Column(Float, default=0.0) # 0.0 to 1.0
    severity = Column(String, default="medium") # low, medium, high, critical
    
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    tags = Column(Text, nullable=True) # JSON or comma-separated tags
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<IOC(value={self.value}, type={self.type}, source={self.source})>"
