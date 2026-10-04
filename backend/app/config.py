from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Application Metadata
    APP_NAME: str = "Specter"
    API_V1_PREFIX: str = "/api"

    # Application Security & RBAC
    JWT_SECRET: str = "placeholder_jwt_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 480
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Relational Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"
    POSTGRES_DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/db"
    POSTGRES_SYNC_DATABASE_URL: str = "postgresql://user:password@localhost/db?sslmode=require"

    # Graph Database Settings
    NEO4J_URI: str = "neo4j+s://localhost"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    USE_IN_MEMORY_GRAPH: bool = False

    # Cache & Queues
    REDIS_URL: str = "redis://localhost:6379/0"

    # Grounded AI Settings
    AI_PROVIDER: str = "local_mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = "grounded-threat-assistant-v1"
    AI_MAX_TOKENS: int = 2048

    # Forensic Evidence Vault
    EVIDENCE_VAULT_DIR: str = "./data/evidence_vault"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Demonstration Mode
    DEMO_LAB_MODE: bool = True

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


settings = Settings()
