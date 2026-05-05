from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SynapseAI Business Copilot"
    API_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./synapseai.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BACKEND_CORS_ORIGINS: list[AnyHttpUrl | str] = ["http://localhost:3000", "http://localhost:5173"]
    STORAGE_BACKEND: str = "local"
    UPLOAD_DIR: Path = Path("storage/uploads")
    MAX_UPLOAD_MB: int = 25

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str] | str:
        if isinstance(value, str) and value:
            return [origin.strip() for origin in value.split(",")]
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
