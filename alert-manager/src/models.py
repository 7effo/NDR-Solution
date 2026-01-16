"""
Database models for Alert Management
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Case(Base):
    """
    Security Case / Incident
    """
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="open", index=True) # open, investigating, resolved, closed
    severity = Column(String, default="medium") # low, medium, high, critical
    assignee = Column(String, nullable=True) # user email
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    artifacts = relationship("CaseArtifact", back_populates="case")
    comments = relationship("CaseComment", back_populates="case")
    alerts = relationship("Alert", back_populates="case")

class CaseArtifact(Base):
    """
    Artifacts related to a case (IPs, domains, etc.)
    """
    __tablename__ = "case_artifacts"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    artifact_type = Column(String, nullable=False) # ip, domain, file_hash
    value = Column(String, nullable=False)
    
    case = relationship("Case", back_populates="artifacts")

class CaseComment(Base):
    """
    Comments/Notes on a case
    """
    __tablename__ = "case_comments"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    user = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="comments")

class Alert(Base):
    """
    Correlated Alert
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    
    alert_id = Column(String, unique=True, index=True) # From OpenSearch _id
    signature = Column(String)
    severity = Column(String)
    category = Column(String)
    
    source_ip = Column(String)
    dest_ip = Column(String)
    dest_port = Column(Integer, nullable=True)
    protocol = Column(String)
    
    timestamp = Column(DateTime)
    raw_data = Column(JSON) # Store full source
    status = Column(String, default="new")
    
    case = relationship("Case", back_populates="alerts")
