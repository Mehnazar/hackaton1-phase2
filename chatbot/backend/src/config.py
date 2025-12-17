"""Configuration management for RAG Chatbot backend."""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Qdrant Cloud Configuration
    qdrant_url: str = Field(..., description="Qdrant Cloud cluster URL")
    qdrant_api_key: str = Field(..., description="Qdrant Cloud API key")

    # Neon Serverless Postgres Configuration
    neon_database_url: str | None = Field(
        None, description="Neon Postgres connection URL (optional)"
    )
    enable_logging: bool = Field(False, description="Enable query/response logging")

    # OpenAI API Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_embedding_model: str = Field(
        "text-embedding-3-small", description="OpenAI embedding model"
    )
    openai_chat_model: str = Field("gpt-4", description="OpenAI chat model")

    # Application Configuration
    environment: str = Field("development", description="Environment (development/production)")
    log_level: str = Field("INFO", description="Logging level")
    admin_api_key: str = Field(..., description="API key for admin endpoints")

    # Chunking Configuration
    chunk_size: int = Field(800, ge=100, le=2000, description="Target chunk size in tokens")
    chunk_overlap: int = Field(
        100, ge=0, le=500, description="Overlap between chunks in tokens"
    )

    # Retrieval Configuration
    top_k_retrieval: int = Field(10, ge=1, le=50, description="Number of chunks to retrieve")
    top_k_rerank: int = Field(5, ge=1, le=20, description="Number of chunks after reranking")
    similarity_threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum similarity for retrieval"
    )
    confidence_threshold: float = Field(
        0.6, ge=0.0, le=1.0, description="Minimum confidence for generation"
    )

    # Performance Configuration
    max_concurrent_requests: int = Field(
        100, ge=1, le=1000, description="Maximum concurrent requests"
    )
    request_timeout_sec: int = Field(30, ge=1, le=300, description="Request timeout in seconds")

    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Allowed CORS origins (comma-separated)",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        if isinstance(self.allowed_origins, str):
            return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
        return self.allowed_origins

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        valid_envs = ["development", "production", "test"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v_lower

    def validate_required_fields(self) -> None:
        """Validate that all required fields are set."""
        required_fields = {
            "qdrant_url": self.qdrant_url,
            "qdrant_api_key": self.qdrant_api_key,
            "openai_api_key": self.openai_api_key,
            "admin_api_key": self.admin_api_key,
        }

        missing_fields = [
            field_name for field_name, value in required_fields.items() if not value
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required configuration fields: {', '.join(missing_fields)}"
            )

        # Validate logging configuration
        if self.enable_logging and not self.neon_database_url:
            raise ValueError(
                "NEON_DATABASE_URL must be set when ENABLE_LOGGING is true"
            )


# Global settings instance
settings = Settings()

# Validate required fields on import
settings.validate_required_fields()
