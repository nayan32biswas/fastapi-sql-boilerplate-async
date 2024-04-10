from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


def new_async_engine(uri: URL) -> AsyncEngine:
    return create_async_engine(
        uri,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30.0,
        pool_recycle=600,
    )


def get_async_session() -> AsyncSession:
    async_engine = new_async_engine(settings.DB_URL)

    return async_sessionmaker(async_engine, expire_on_commit=False)()


class Base(DeclarativeBase): ...
