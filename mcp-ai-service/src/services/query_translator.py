"""
Natural language query translator
Converts natural language queries to OpenSearch DSL
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

import structlog
from openai import AsyncOpenAI

from ..config import settings

logger = structlog.get_logger()


class QueryTranslator:
    """Translates natural language queries to OpenSearch DSL"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
    async def translate(self, natural_query: str, index_pattern: str = "*") -> Dict[str, Any]:
        """
        Translate natural language query to OpenSearch DSL
        
        Args:
            natural_query: Natural language query from user
            index_pattern: OpenSearch index pattern to search
            
        Returns:
            OpenSearch query DSL
        """
        logger.info("Translating query", query=natural_query, index=index_pattern)
        
        if not self.client:
            # Fallback to simple keyword matching if no AI available
            return self._fallback_translation(natural_query)
        
        # Build prompt for query translation
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(natural_query, index_pattern)
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.MCP_AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.MCP_AI_TEMPERATURE,
                max_tokens=settings.MCP_AI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Query translated successfully", opensearch_query=result)
            
            return result
            
        except Exception as e:
            logger.error("Query translation failed", error=str(e))
            return self._fallback_translation(natural_query)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for query translation"""
        return """You are an expert in translating natural language queries into OpenSearch Query DSL.

Your task is to convert user questions about network security data into valid OpenSearch queries.

Common fields in our data:
- Zeek logs: @timestamp, id.orig_h (source IP), id.resp_h (dest IP), id.resp_p (dest port), 
  proto (protocol), service, conn_state, duration, orig_bytes, resp_bytes
- Suricata alerts: @timestamp, src_ip, dest_ip, dest_port, alert.signature, alert.severity, alert.category
- General: host.name, host.ip, event.category, event.action, user.name

Time ranges:
- "last hour" = now-1h
- "last 24 hours" = now-24h  
- "last 7 days" = now-7d
- "today" = now/d

Return ONLY valid JSON with this structure:
{
  "query": { ... OpenSearch query DSL ... },
  "size": 100,
  "sort": [{"@timestamp": {"order": "desc"}}],
  "explanation": "plain English explanation of what this query does"
}"""

    def _build_user_prompt(self, query: str, index_pattern: str) -> str:
        """Build user prompt for query translation"""
        return f"""Convert this question to an OpenSearch query:

Question: {query}
Index pattern: {index_pattern}

Return the OpenSearch query DSL as JSON."""

    def _fallback_translation(self, query: str) -> Dict[str, Any]:
        """Fallback translation using simple keyword matching"""
        logger.warning("Using fallback query translation")
        
        # Extract time range
        time_range = self._extract_time_range(query)
        
        # Build simple query_string query
        opensearch_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": query,
                                "default_operator": "AND"
                            }
                        }
                    ],
                    "filter": [
                        {
                            "range": {
                                "@timestamp": time_range
                            }
                        }
                    ]
                }
            },
            "size": settings.DEFAULT_QUERY_SIZE,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        return opensearch_query
    
    def _extract_time_range(self, query: str) -> Dict[str, str]:
        """Extract time range from natural language query"""
        query_lower = query.lower()
        
        if "last hour" in query_lower or "past hour" in query_lower:
            return {"gte": "now-1h", "lte": "now"}
        elif "last 24 hours" in query_lower or "last day" in query_lower:
            return {"gte": "now-24h", "lte": "now"}
        elif "last 7 days" in query_lower or "last week" in query_lower:
            return {"gte": "now-7d", "lte": "now"}
        elif "last 30 days" in query_lower or "last month" in query_lower:
            return {"gte": "now-30d", "lte": "now"}
        elif "today" in query_lower:
            return {"gte": "now/d", "lte": "now"}
        else:
            # Default to last 24 hours
            return {"gte": "now-24h", "lte": "now"}
