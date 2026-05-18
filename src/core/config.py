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
    frontend_origins: str = ""
    frontend_origin_scheme: str = "http"
    frontend_origin_hosts: str = "localhost:5173,127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    @property
    def frontend_origins_list(self) -> list[str]:
        if self.frontend_origins.strip():
            return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

        return [
            f"{self.frontend_origin_scheme}://{host.strip()}"
            for host in self.frontend_origin_hosts.split(",")
            if host.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
