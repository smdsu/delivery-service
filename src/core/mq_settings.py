from pathlib import Path


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitMQSettings(BaseSettings):
    DEFAULT_USER: str = Field(default="admin")
    DEFAULT_PASS: str = Field(default="admin")
    DEFAULT_VHOST: str = Field(default="/")
    PORT: int = Field(default=5672, ge=1, le=65535)
    MANAGEMENT_PORT: int = Field(default=15672, ge=1, le=65535)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        env_prefix="RABBITMQ_",
        extra="ignore",
    )

    def get_mq_url(self) -> str:
        vhost = "/" if self.DEFAULT_VHOST == "/" else self.DEFAULT_VHOST
        return (
            f"amqp://{self.DEFAULT_USER}:"
            f"{self.DEFAULT_PASS}@rabbitmq:{self.PORT}"
            f"{vhost}"
        )


mq_settings = RabbitMQSettings()
