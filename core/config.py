import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

DB_ASYNC_TO_SYNC_MODULE = ("asyncpg", "psycopg2")  # postgresql
# DB_ASYNC_TO_SYNC_MODULE = ("+aiosqlite", "")  # sqlite
# DB_ASYNC_TO_SYNC_MODULE = ("aiomysql", "pymysql")  # mysql


class Settings(BaseSettings):
    DEBUG: bool = True
    ENV: str = "development"
    APP_HOST: str = "localhost:3000"
    API_HOST: str = "localhost:8000"

    DB_URL: str = "postgresql+asyncpg://sqluser:password@localhost:5432/fastapi_sql_db"

    JWT_SECRET_KEY: str = "fastapi"

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_BACKEND_URL: str = "redis://redis:6379/0"
    CELERY_CONCURRENCY: int = 2


class TestSettings(Settings):
    DB_URL: str = "postgresql+asyncpg://sqluser:password@localhost:5432/fastapi_sql_db"


class LocalSettings(Settings): ...


class ProductionSettings(Settings):
    DEBUG: bool = False
    ENV: str = "production"


@lru_cache(maxsize=1)
def get_settings():
    env = os.getenv("ENV", "local")
    config_type = {
        "test": TestSettings(),
        "local": LocalSettings(),
        "prod": ProductionSettings(),
    }
    return config_type[env]


settings: Settings = get_settings()
