"""
Application Configuration

Centralized configuration management using Pydantic settings.
All environment variables and application settings are defined here.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application Settings
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database
    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_RPM: int = 3000
    
    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str = "career-coach-index"
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_RPM: int = 1000
    
    # SerpAPI
    SERPAPI_API_KEY: str
    SERPAPI_RPM: int = 100
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    UPLOAD_PATH: str = "./uploads"
    TEMP_PATH: str = "./temp"
    
    # Voice Processing
    AUDIO_FORMAT: str = "wav"
    AUDIO_SAMPLE_RATE: int = 16000
    MAX_AUDIO_DURATION_SECONDS: int = 300
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    ENABLE_VOICE_FEATURES: bool = True
    ENABLE_SIMULATION_ENGINE: bool = True
    ENABLE_CAREER_ANALYTICS: bool = True
    ENABLE_REAL_TIME_UPDATES: bool = True
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(settings.TEMP_PATH, exist_ok=True)
