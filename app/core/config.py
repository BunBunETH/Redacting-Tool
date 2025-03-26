from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Intercom Data Security System"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Intercom
    INTERCOM_ACCESS_TOKEN: str = os.getenv("INTERCOM_ACCESS_TOKEN", "")
    INTERCOM_WEBHOOK_SECRET: str = os.getenv("INTERCOM_WEBHOOK_SECRET", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ML Model Settings
    MODEL_CONFIDENCE_THRESHOLD: float = float(os.getenv("MODEL_CONFIDENCE_THRESHOLD", "0.85"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "1.0.0")
    
    # DLP Settings
    BLOCK_EXTERNAL_MESSAGES: bool = os.getenv("BLOCK_EXTERNAL_MESSAGES", "true").lower() == "true"
    NOTIFY_ADMIN_ON_BLOCK: bool = os.getenv("NOTIFY_ADMIN_ON_BLOCK", "true").lower() == "true"
    ENABLE_ML_DETECTION: bool = os.getenv("ENABLE_ML_DETECTION", "true").lower() == "true"
    ENABLE_REGEX_DETECTION: bool = os.getenv("ENABLE_REGEX_DETECTION", "true").lower() == "true"
    
    # Vault Settings
    VAULT_BASE_URL: str = os.getenv("VAULT_BASE_URL", "https://vault.example.com")
    VAULT_RETENTION_DAYS: int = int(os.getenv("VAULT_RETENTION_DAYS", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_ACCESS_LOGS: bool = os.getenv("ENABLE_ACCESS_LOGS", "true").lower() == "true"
    
    class Config:
        case_sensitive = True

settings = Settings() 