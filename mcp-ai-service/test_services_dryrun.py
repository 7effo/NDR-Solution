import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock config settings
sys.modules['src.config'] = MagicMock()
sys.modules['src.config'].settings = MagicMock()
sys.modules['src.config'].settings.OPENSEARCH_HOST = "localhost"
sys.modules['src.config'].settings.OPENSEARCH_PORT = 9200
sys.modules['src.config'].settings.OPENSEARCH_USER = "admin"
sys.modules['src.config'].settings.OPENSEARCH_PASSWORD = "admin"

from src.services.threat_hunting import ThreatHuntingService
from src.services.incident_response import IncidentResponseService
from src.services.opensearch_client import OpenSearchClient
from src.routes.tools import InvestigateIPRequest, RemediationRequest

async def test_services():
    print("Testing Service Instantiation...")
    
    # Mock OpenSearch Client
    mock_os_client = MagicMock(spec=OpenSearchClient)
    
    # Test Threat Hunting Service
    th_service = ThreatHuntingService(mock_os_client)
    assert th_service.os_client == mock_os_client
    print("ThreatHuntingService initialized successfully")
    
    # Test Incident Response Service
    ir_service = IncidentResponseService()
    print("IncidentResponseService initialized successfully")
    
    # Test Request Models
    req = InvestigateIPRequest(ip_address="1.2.3.4")
    assert req.ip_address == "1.2.3.4"
    print("Request models valid")

if __name__ == "__main__":
    asyncio.run(test_services())
