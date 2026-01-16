"""
Configuration for API Gateway
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API Gateway settings"""
    
    # Application
    VERSION: str = "0.1.0-alpha"
    DEBUG: bool = False
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    
    # Database (PostgreSQL)
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "thunderx"
    POSTGRES_USER: str = "thunderx"
    POSTGRES_PASSWORD: str
    
    # OpenSearch
    OPENSEARCH_HOST: str = "opensearch-node1"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str
    OPENSEARCH_USE_SSL: bool = True
    OPENSEARCH_VERIFY_CERTS: bool = False
    
    # MCP AI Service
    MCP_AI_SERVICE_URL: str = "http://mcp-ai-service:5000"
    
    # Alert Manager
    ALERT_MANAGER_URL: str = "http://alert-manager:6000"
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Database URL
DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
