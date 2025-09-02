from pathlib import Path
from typing import AsyncGenerator


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)


class DatabaseSettings(BaseSettings):
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=5432, ge=1, le=65535)
    DB: str = Field(min_length=1)
    USER: str = Field(min_length=1)
    PASSWORD: str = Field(min_length=1)

    POOL_SIZE: int = Field(default=10, ge=1)
    MAX_OVERFLOW: int = Field(default=20, ge=0)
    ECHO: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        env_prefix="POSTGRES_",
        extra="ignore",
    )

    def get_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USER}:"
            f"{self.PASSWORD}@{self.HOST}:"
            f"{self.PORT}/{self.DB}"
        )


class DatabaseManager:
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(
                self.settings.get_database_url(),
                pool_size=self.settings.POOL_SIZE,
                max_overflow=self.settings.MAX_OVERFLOW,
                echo=self.settings.ECHO,
                future=True,
            )
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()


db_settings = DatabaseSettings()  # type: ignore[call-arg]
db_manager = DatabaseManager(db_settings)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
