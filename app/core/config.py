from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, NonNegativeFloat, PositiveInt, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="License Insight Scraper API")
    app_env: Literal["local", "development", "staging", "production"] = Field(default="local")
    app_debug: bool = Field(default=False)
    api_prefix: str = Field(default="/api/v1")

    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:8000"])

    scraper_login_url: AnyHttpUrl = Field(
        default="https://balcaovirtual.inatro.gov.mz/app/ajax/auth/login.php"
    )
    scraper_license_status_url: AnyHttpUrl = Field(
        default="https://balcaovirtual.inatro.gov.mz/estado_carta.php"
    )
    scraper_driving_ticket_url: AnyHttpUrl = Field(
        default="https://balcaovirtual.inatro.gov.mz/consulta_multas.php"
    )
    scraper_timeout_seconds: NonNegativeFloat = Field(default=20.0)
    scraper_max_retries: PositiveInt = Field(default=3)
    scraper_backoff_multiplier: NonNegativeFloat = Field(default=0.8)
    scraper_proxy_url: str | None = Field(default=None)
    scraper_verify_ssl: bool = Field(default=True)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("scraper_proxy_url", mode="before")
    @classmethod
    def empty_proxy_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
