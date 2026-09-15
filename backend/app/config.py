from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AutomatizoCX"
    app_version: str = "2.0.0"
    environment: str = "development"
    database_url: str = "sqlite:///./data/automatizo_cx.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    handoff_webhook_url: str | None = None
    admin_api_key: str = "change-me-before-production"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    rate_limit_per_minute: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def ensure_data_directory() -> None:
    if settings.database_url.startswith("sqlite:///./"):
        relative_path = settings.database_url.removeprefix("sqlite:///./")
        Path(relative_path).parent.mkdir(parents=True, exist_ok=True)
