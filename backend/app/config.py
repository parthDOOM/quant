"""
Configuration management for the application.
Loads settings from environment variables and .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator, ValidationError
from typing import List
from functools import lru_cache
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Quantitative Strategy & Risk Dashboard"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    cache_ttl: int = 3600
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/quant_db"
    db_echo: bool = False
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """
        Validate database URL doesn't contain weak credentials.
        """
        environment = info.data.get('environment', 'development')
        
        # Check for common weak passwords in connection string
        weak_passwords = ["password", "admin", "root", "test", "changeme"]
        
        if environment == "production":
            for weak_pwd in weak_passwords:
                if weak_pwd in v.lower():
                    raise ValueError(
                        f"Database URL contains weak password '{weak_pwd}' in production! "
                        "Use strong credentials and store them in environment variables."
                    )
        else:
            for weak_pwd in weak_passwords:
                if weak_pwd in v.lower():
                    logger.warning(
                        f"WARNING: Database URL contains weak password in {environment}. "
                        "This is OK for development but MUST be changed for production!"
                    )
                    break
        
        return v
    
    # JWT Authentication
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """
        Validate that secret_key is strong enough for production.
        Warns in development, fails in production.
        """
        # Get environment from values being validated
        environment = info.data.get('environment', 'development')
        
        # Check for default/weak secrets
        weak_secrets = [
            "your-secret-key-change-this-in-production",
            "secret",
            "password",
            "changeme",
            "test"
        ]
        
        is_weak = (
            v.lower() in weak_secrets or
            len(v) < 32 or
            v.isalnum() and len(set(v)) < 10  # Too simple, not enough entropy
        )
        
        if is_weak:
            if environment == "production":
                raise ValueError(
                    "SECRET_KEY is too weak for production! "
                    "Use a strong random key with at least 32 characters, "
                    "including letters, numbers, and special characters. "
                    f"Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
            else:
                logger.warning(
                    f"WARNING: Using weak SECRET_KEY in {environment} environment. "
                    "This is OK for development but MUST be changed for production!"
                )
        
        return v
    
    # Financial Data
    default_start_date: str = "2022-01-01"
    default_lookback_days: int = 730
    yfinance_timeout: int = 30
    
    # HRP Settings
    default_linkage_method: str = "ward"
    min_correlation_periods: float = 0.8
    default_p_value_threshold: float = 0.05
    
    # Risk-Free Rate
    risk_free_rate: float = 0.05
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()
