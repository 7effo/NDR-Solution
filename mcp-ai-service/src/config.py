"""
Configuration settings for ThunderX MCP AI Service
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    VERSION: str = "0.1.0-alpha"
    DEBUG: bool = False
    PORT: int = 5000
    LOG_LEVEL: str = "INFO"
    
    # OpenSearch
    OPENSEARCH_HOST: str = "opensearch-node1"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_MCP_PORT: int = 3000
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str
    OPENSEARCH_USE_SSL: bool = True
    OPENSEARCH_VERIFY_CERTS: bool = False
    
    # MCP
    MCP_AI_MODEL: str = "gpt-4"
    MCP_AI_TEMPERATURE: float = 0.3
    MCP_AI_MAX_TOKENS: int = 2000
    
    # OpenAI (if using OpenAI models)
    OPENAI_API_KEY: str = ""
    
    # Anthropic (if using Claude)
    ANTHROPIC_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Query settings
    MAX_QUERY_RESULTS: int = 10000
    DEFAULT_QUERY_SIZE: int = 100
    QUERY_TIMEOUT_SECONDS: int = 30
    
    # Threat hunting
    THREAT_HUNTING_ENABLED: bool = True
    CORRELATION_WINDOW_MINUTES: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
