"""
Configuration for Detection Engine
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VERSION: str = "0.1.0-alpha"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # dependencies
    OPENSEARCH_HOST: str = "opensearch-node1"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str
    
    ALERT_MANAGER_URL: str = "http://alert-manager:6000"
    
    # Detection
    RUN_INTERVAL_SECONDS: int = 60
    RULE_PATH: str = "rules"
    
    class Config:
        env_file = ".env"

settings = Settings()
