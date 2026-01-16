"""
Detection Engine Main Service
Runs scheduled queries against OpenSearch to detect threats
"""
import asyncio
import structlog
import httpx
from datetime import datetime, timedelta
from opensearchpy import AsyncOpenSearch

from .config import settings
from .rules_loader import RuleLoader

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

class DetectionEngine:
    def __init__(self):
        self.rules = []
        self.loader = RuleLoader(settings.RULE_PATH)
        
        self.os_client = AsyncOpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )
        
    async def load_rules(self):
        """Reload rules"""
        self.rules = self.loader.load_rules()

    async def run(self):
        """Main loop"""
        logger.info("Starting Detection Engine")
        await self.load_rules()
        
        while True:
            start_time = datetime.utcnow()
            await self.run_cycle()
            
            # Simple sleep for interval
            await asyncio.sleep(settings.RUN_INTERVAL_SECONDS)

    async def run_cycle(self):
        """Execute one cycle of all rules"""
        for rule in self.rules:
            try:
                await self.execute_rule(rule)
            except Exception as e:
                logger.error("Error executing rule", rule=rule['name'], error=str(e))

    async def execute_rule(self, rule):
        """Execute a single rule"""
        # Time window
        now = datetime.utcnow()
        lookback = rule.get('lookback_minutes', 5)
        start_time = (now - timedelta(minutes=lookback)).isoformat()
        
        # Build Query
        query = {
            "query": {
                "bool": {
                    "must": [
                        # Use the rule's custom DSL
                        rule['query_dsl'],
                        {"range": {"timestamp": {"gte": start_time}}}
                    ]
                }
            },
            "size": 0, # We mostly care about aggs first
            "aggs": rule.get('aggregations', {})
        }
        
        # Search
        response = await self.os_client.search(
            index=rule['index'],
            body=query
        )
        
        # Evaluate Condition
        # Basic implementation: Check aggregation buckets
        # "condition": {"type": "count_greater_than", "threshold": 5, "agg_field": "src_ip"}
        condition = rule.get('condition')
        
        if condition['type'] == 'count_greater_than':
            agg_name = list(rule['aggregations'].keys())[0] # Assume first agg
            buckets = response['aggregations'][agg_name]['buckets']
            
            for bucket in buckets:
                if bucket['doc_count'] > condition['threshold']:
                    # ALERT!
                    entity_value = bucket['key']
                    await self.trigger_alert(rule, entity_value, bucket['doc_count'])

    async def trigger_alert(self, rule, entity, count):
        """Send alert to Alert Manager"""
        logger.warn("Rule Triggered", rule=rule['name'], entity=entity, count=count)
        
        payload = {
            "title": f"Detection: {rule['name']} ({entity})",
            "description": f"Rule '{rule['name']}' triggered. Found {count} events for {entity} in last {rule.get('lookback_minutes', 5)}m.\n\nDescription: {rule.get('description')}",
            "severity": rule['severity']
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{settings.ALERT_MANAGER_URL}/cases", json=payload)
            except Exception as e:
                logger.error("Failed to send alert", error=str(e))

if __name__ == "__main__":
    engine = DetectionEngine()
    asyncio.run(engine.run())
