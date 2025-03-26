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
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/intercom_security")
    
    # Intercom
    INTERCOM_ACCESS_TOKEN: str = os.getenv("INTERCOM_ACCESS_TOKEN", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ML Model Settings
    MODEL_CONFIDENCE_THRESHOLD: float = 0.85
    MAX_TOKENS: int = 1000
    
    # DLP Settings
    BLOCK_EXTERNAL_MESSAGES: bool = True
    NOTIFY_ADMIN_ON_BLOCK: bool = True
    
    class Config:
        case_sensitive = True

settings = Settings() 