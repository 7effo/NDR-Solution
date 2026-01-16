"""
Threat Hunting Service
Provides advanced investigation capabilities for security analysis
"""

from typing import Dict, Any, List
import structlog
from .opensearch_client import OpenSearchClient

logger = structlog.get_logger()

class ThreatHuntingService:
    def __init__(self, opensearch_client: OpenSearchClient):
        self.os_client = opensearch_client

    async def investigate_ip(self, ip_address: str, time_range: str = "now-24h") -> Dict[str, Any]:
        """
        Investigate an IP address across all data sources
        """
        logger.info("Starting IP investigation", ip=ip_address)
        
        # 1. Search for Zeek connections involving this IP
        zeek_query = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"id.orig_h": ip_address}},
                        {"term": {"id.resp_h": ip_address}}
                    ],
                    "minimum_should_match": 1
                }
            },
            "size": 50,
            "sort": [{"@timestamp": "desc"}]
        }
        
        zeek_results = await self.os_client.search("zeek-*", zeek_query)
        
        # 2. Search for Suricata alerts
        suricata_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"event_type": "alert"}},
                        {"bool": {
                            "should": [
                                {"term": {"src_ip": ip_address}},
                                {"term": {"dest_ip": ip_address}}
                            ]
                        }}
                    ]
                }
            },
            "size": 20,
            "sort": [{"timestamp": "desc"}]
        }
        
        suricata_results = await self.os_client.search("suricata-*", suricata_query)
        
        return {
            "ip": ip_address,
            "summary": {
                "connection_count": zeek_results['hits']['total']['value'],
                "alert_count": suricata_results['hits']['total']['value']
            },
            "recent_connections": [h['_source'] for h in zeek_results['hits']['hits']],
            "recent_alerts": [h['_source'] for h in suricata_results['hits']['hits']]
        }

    async def find_lateral_movement(self, source_ip: str) -> List[Dict[str, Any]]:
        """
        Detect potential lateral movement from a source IP
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"id.orig_h": source_ip}},
                        {"terms": {"service": ["ssh", "rdp", "smb", "krb5"]}}
                    ]
                }
            },
            "size": 100
        }
        
        results = await self.os_client.search("zeek-*", query)
        return [h['_source'] for h in results['hits']['hits']]
