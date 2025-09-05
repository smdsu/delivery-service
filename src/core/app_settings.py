from pathlib import Path
import secrets

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Настройки приложения"""

    # Основные настройки
    NAME: str = Field(default="Delivery Service")
    VERSION: str = Field(default="v0.0.1")
    TIMEZONE: str = Field(default="UTC")
    DESCRIPTION: str = Field(default="")
    DEBUG: bool = Field(default=True)

    # Настройки безопасности
    SECRET_KEY: SecretStr = Field(min_length=32)
    ALGORITHM: str
    ENCRYPTION_KEY: SecretStr = Field(min_length=32)

    # Настройки токенов
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, ge=1)

    # Настройки CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
    )

    # Настройки API
    API_V1_PREFIX: str = Field(default="/api/v1")
    DOCS_URL: str | None = Field(default="/docs")
    REDOC_URL: str | None = Field(default="/redoc")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
        case_sensitive=True,
    )

    @staticmethod
    def generate_secret_key() -> str:
        return secrets.token_urlsafe(32)

    def get_cors_config(self) -> dict:
        return {
            "allow_origins": self.CORS_ORIGINS,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


app_settings = AppSettings()  # type: ignore[call-arg]
