"""
Feed Manager
Handles fetching and parsing of threat intelligence feeds
"""

import logging
import asyncio
from datetime import datetime
import httpx
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .models import IOC
from .config import settings

logger = logging.getLogger(__name__)

class FeedManager:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def update_all_feeds(self):
        """Update all configured feeds"""
        logger.info("Starting feed update...")
        await self.fetch_threatfox()
        # await self.fetch_abuseipdb() # Requires API Key
        logger.info("Feed update complete.")

    async def fetch_threatfox(self):
        """Fetch recent IOCs from ThreatFox (Abuse.ch)"""
        url = "https://threatfox-api.abuse.ch/api/v1/"
        payload = {
            "query": "get_iocs",
            "days": 1
        }
        
        try:
            logger.info("Fetching ThreatFox feed...")
            response = await self.http_client.post(url, json=payload)
            data = response.json()
            
            if data.get("query_status") != "ok":
                logger.warning(f"ThreatFox error: {data.get('query_status')}")
                return

            iocs = data.get("data", [])
            count = 0
            
            for item in iocs:
                ioc_value = item.get("ioc")
                ioc_type = item.get("ioc_type")
                
                # Normalize type
                if "ip" in ioc_type:
                    ioc_type = "ip"
                elif "domain" in ioc_type:
                    ioc_type = "domain"
                
                confidence = float(item.get("confidence_level", 0)) / 100.0
                
                # Upsert IOC
                stmt = insert(IOC).values(
                    value=ioc_value,
                    type=ioc_type,
                    source="threatfox",
                    confidence=confidence,
                    severity="high", # Default for ThreatFox
                    tags=item.get("tags"),
                    last_seen=datetime.utcnow()
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=['value'],
                    set_=dict(
                        last_seen=datetime.utcnow(),
                        confidence=stmt.excluded.confidence
                    )
                )
                self.db.execute(stmt)
                count += 1
            
            self.db.commit()
            logger.info(f"Imported {count} IOCs from ThreatFox")
            
        except Exception as e:
            logger.error(f"Failed to fetch ThreatFox: {e}")
            self.db.rollback()

    async def close(self):
        await self.http_client.aclose()
