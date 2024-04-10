import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

DB_ASYNC_TO_SYNC_MODULE = ("asyncpg", "psycopg2")  # postgresql
# DB_ASYNC_TO_SYNC_MODULE = ("+aiosqlite", "")  # sqlite
# DB_ASYNC_TO_SYNC_MODULE = ("aiomysql", "pymysql")  # mysql


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DB_URL: str = "postgresql+asyncpg://sqluser:password@localhost:5432/fastapi_sql_db"

    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


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
