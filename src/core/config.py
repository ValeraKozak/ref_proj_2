import secrets
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bulletin Board Platform"
    app_env: str = "development"
    database_url: str = "mongodb://localhost:27017/bulletin_board"
    upload_dir: str = "uploads"
    uploads_url_prefix: str = "/uploads"
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    log_level: str = "INFO"
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
