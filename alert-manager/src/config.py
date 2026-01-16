"""
Configuration for Alert Manager Service
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    VERSION: str = "0.1.0-alpha"
    DEBUG: bool = False
    PORT: int = 6000
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
    POSTGRES_PORT: int = 5432
    
    # Correlation
    CORRELATION_INTERVAL_SECONDS: int = 60
    MIN_SEVERITY_TO_ALERT: int = 3 # 1=High, 2=Medium, 3=Low in Suricata
    
    class Config:
        env_file = ".env"

settings = Settings()
