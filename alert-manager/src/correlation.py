"""
Correlation Engine
Analyzes alerts from OpenSearch and correlates them into cases
"""
import structlog
import asyncio
from datetime import datetime, timedelta
from opensearchpy import AsyncOpenSearch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from .config import settings
from .models import Case, Alert, Base

logger = structlog.get_logger()

class CorrelationEngine:
    def __init__(self):
        # OpenSearch client
        self.os_client = AsyncOpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )
        
        # Database connection
        db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        self.engine = create_async_engine(db_url, echo=settings.DEBUG)
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
    async def run_correlation_cycle(self):
        """Main correlation loop"""
        logger.info("Starting correlation cycle")
        try:
            # 1. Fetch high severity alerts from last minute from OpenSearch
            alerts = await self.fetch_recent_alerts()
            
            if alerts:
                logger.info("Found recent alerts", count=len(alerts))
                await self.process_alerts(alerts)
                
        except Exception as e:
            logger.error("Error in correlation cycle", error=str(e))

    async def fetch_recent_alerts(self):
        """Query OpenSearch for recent Suricata alerts"""
        # Look back 2 minutes to be safe
        now = datetime.utcnow()
        start_time = (now - timedelta(minutes=2)).isoformat()
        
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "alert"}},
                        {"range": {"timestamp": {"gte": start_time}}}
                    ]
                }
            },
            "size": 100
        }
        
        try:
            response = await self.os_client.search(
                index="suricata-*",
                body=query
            )
            return response['hits']['hits']
        except Exception as e:
            logger.error("OpenSearch query failed", error=str(e))
            return []

    async def process_alerts(self, hits):
        """Process raw alerts and create cases if needed"""
        async with self.AsyncSessionLocal() as session:
            for hit in hits:
                source = hit['_source']
                alert_data = source.get('alert', {})
                
                # Filter by severity (1 is highest in Suricata)
                severity = alert_data.get('severity', 3)
                if severity > settings.MIN_SEVERITY_TO_ALERT:
                    continue
                
                # Check if alert already exists in DB
                alert_id = hit['_id']
                existing = await session.execute(select(Alert).where(Alert.alert_id == alert_id))
                if existing.scalar_one_or_none():
                    continue
                
                # Create basic alert record
                new_alert = Alert(
                    alert_id=alert_id,
                    signature=alert_data.get('signature'),
                    severity=str(severity),
                    category=alert_data.get('category'),
                    source_ip=source.get('src_ip'),
                    dest_ip=source.get('dest_ip'),
                    dest_port=source.get('dest_port'),
                    protocol=source.get('proto'),
                    timestamp=datetime.fromisoformat(source.get('timestamp').replace('Z', '+00:00')),
                    raw_data=source,
                    status='new'
                )
                
                # Correlation Logic: Group by Source IP
                # Check for active open case with same Source IP
                stmt = select(Case).where(
                    Case.status == 'open',
                    Case.description.contains(source.get('src_ip'))
                )
                result = await session.execute(stmt)
                existing_case = result.scalars().first()
                
                if existing_case:
                    # Attach to existing case
                    new_alert.case_id = existing_case.id
                    logger.info("Attached alert to existing case", case_id=existing_case.id, alert=new_alert.signature)
                else:
                    # Create new case
                    new_case = Case(
                        title=f"Suspicious Activity from {source.get('src_ip')}",
                        description=f"Automated case created for IP {source.get('src_ip')}. First alert: {alert_data.get('signature')}",
                        severity="high" if severity == 1 else "medium",
                        status="open"
                    )
                    session.add(new_case)
                    await session.flush() # Get ID
                    
                    new_alert.case_id = new_case.id
                    logger.info("Created new case", case_id=new_case.id, alert=new_alert.signature)
                
                session.add(new_alert)
            
            await session.commit()
