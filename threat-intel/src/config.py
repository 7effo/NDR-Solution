"""
Configuration for Threat Intel Service
"""
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VERSION: str = "0.1.0-alpha"
    DEBUG: bool = False
    PORT: int = 7000
    LOG_LEVEL: str = "INFO"
    
    # dependencies
    OPENSEARCH_HOST: str = "opensearch-node1"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str
    
    # Postgres
    POSTGRES_HOST: str = "postgres"
    POSTGRES_DB: str = "thunderx"
    POSTGRES_USER: str = "thunderx"
    POSTGRES_PASSWORD: str

    # Feeds (default enabled feeds)
    ENABLED_FEEDS: List[str] = ["threatfox"]
    UPDATE_INTERVAL_HOURS: int = 24
    
    class Config:
        env_file = ".env"

settings = Settings()
