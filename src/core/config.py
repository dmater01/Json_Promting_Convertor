"""Application configuration management."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "structured-prompt-service"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    cors_origins: List[str] = ["http://localhost:3000"]

    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str
    cache_ttl: int = 3600

    # RabbitMQ
    rabbitmq_url: str

    # LLM Providers
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # LLM Configuration
    default_llm_provider: str = "gemini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048
    llm_timeout: int = 10

    # Rate Limiting
    rate_limit_per_hour: int = 1000
    rate_limit_burst: int = 20

    # Security
    api_key_secret: str
    jwt_secret: str = ""

    # Monitoring
    prometheus_enabled: bool = True
    jaeger_enabled: bool = False
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Feature Flags
    enable_caching: bool = True
    enable_pii_detection: bool = False
    enable_tracing: bool = False


# Global settings instance
settings = Settings()
