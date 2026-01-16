"""
OpenSearch client for ThunderX
"""

from typing import Dict, Any, List, Optional
import structlog
from opensearchpy import AsyncOpenSearch
from opensearchpy.exceptions import OpenSearchException

from ..config import settings

logger = structlog.get_logger()


class OpenSearchClient:
    """OpenSearch client wrapper"""
    
    def __init__(self):
        self.client = AsyncOpenSearch(
            hosts=[{
                'host': settings.OPENSEARCH_HOST,
                'port': settings.OPENSEARCH_PORT
            }],
            http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            ssl_show_warn=False
        )
        
    async def ping(self) -> bool:
        """Check if OpenSearch is reachable"""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("OpenSearch ping failed", error=str(e))
            return False
    
    async def search(
        self,
        index: str,
        body: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a search query
        
        Args:
            index: Index pattern to search
            body: OpenSearch query DSL
            **kwargs: Additional search parameters
            
        Returns:
            Search results
        """
        try:
            response = await self.client.search(
                index=index,
                body=body,
                request_timeout=settings.QUERY_TIMEOUT_SECONDS,
                **kwargs
            )
            return response
        except OpenSearchException as e:
            logger.error("OpenSearch query failed", error=str(e), index=index)
            raise
    
    async def count(self, index: str, body: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching a query
        
        Args:
            index: Index pattern
            body: Optional query DSL
            
        Returns:
            Document count
        """
        try:
            response = await self.client.count(index=index, body=body)
            return response.get('count', 0)
        except OpenSearchException as e:
            logger.error("OpenSearch count failed", error=str(e), index=index)
            return 0
    
    async def get_indices(self) -> List[str]:
        """Get list of all indices"""
        try:
            indices = await self.client.cat.indices(format='json')
            return [idx['index'] for idx in indices if not idx['index'].startswith('.')]
        except OpenSearchException as e:
            logger.error("Failed to get indices", error=str(e))
            return []
    
    async def aggregate(
        self,
        index: str,
        agg_name: str,
        agg_body: Dict[str, Any],
        query: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute an aggregation query
        
        Args:
            index: Index pattern
            agg_name: Aggregation name
            agg_body: Aggregation DSL
            query: Optional filter query
            
        Returns:
            Aggregation results
        """
        body = {
            "size": 0,
            "aggs": {
                agg_name: agg_body
            }
        }
        
        if query:
            body["query"] = query
        
        try:
            response = await self.client.search(index=index, body=body)
            return response.get("aggregations", {}).get(agg_name, {})
        except OpenSearchException as e:
            logger.error("Aggregation failed", error=str(e), index=index)
            raise
    
    async def close(self):
        """Close the client connection"""
        await self.client.close()
