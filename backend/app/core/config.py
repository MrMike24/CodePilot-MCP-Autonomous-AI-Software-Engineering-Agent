from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for CodePilot-MCP application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Core System Settings
    PROJECT_NAME: str = "CodePilot-MCP"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")
    DEMO_MODE: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production-123456789")

    # API Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # PostgreSQL Database
    POSTGRES_USER: str = Field(default="codepilot")
    POSTGRES_PASSWORD: str = Field(default="codepilot_pass")
    POSTGRES_DB: str = Field(default="codepilot_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./codepilot_sqlite.db"
    )

    @property
    def async_database_url(self) -> str:
        """Return proper async DB URL fallback to sqlite for instant local execution if postgres is absent."""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        return self.DATABASE_URL

    # Vector DB (Qdrant)
    QDRANT_HOST: str = Field(default="localhost")
    QDRANT_PORT: int = Field(default=6333)
    QDRANT_COLLECTION_NAME: str = Field(default="codepilot_codebase")
    QDRANT_URL: str | None = Field(default=None)

    # LLM Settings
    LLM_PROVIDER: Literal["openai", "anthropic", "local", "mock"] = Field(default="openai")
    LLM_MODEL: str = Field(default="gpt-4o")
    LLM_API_KEY: str = Field(default="mock-key-demo")
    LLM_TEMPERATURE: float = Field(default=0.0)

    # GitHub API
    GITHUB_TOKEN: str | None = Field(default=None)
    GITHUB_DEFAULT_OWNER: str = Field(default="codepilot-org")
    GITHUB_DEFAULT_REPO: str = Field(default="demo_repository")

    # Docker Execution Sandbox
    DOCKER_SANDBOX_IMAGE: str = Field(default="python:3.12-slim")
    DOCKER_SANDBOX_TIMEOUT: int = Field(default=120)
    DOCKER_SANDBOX_MEMORY_LIMIT: str = Field(default="512m")
    DOCKER_SANDBOX_CPU_LIMIT: float = Field(default=1.0)

    # Security
    ALLOWED_HOST_WORKSPACE_ROOT: str = Field(
        default_factory=lambda: str(Path(__file__).resolve().parents[3] / "demo_repository")
    )


settings = Settings()
