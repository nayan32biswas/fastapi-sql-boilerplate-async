import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as fastapi_app
from app.user.models import User
from core.auth.jwt import JWTProvider
from core.db.session import get_async_session
from tests.data import get_or_create_default_user


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(name="session", scope="function")
async def fixture_session_with_rollback() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session


@pytest_asyncio.fixture(name="client", scope="function")
async def fixture_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.headers.update({"Host": "localhost"})
        yield client


@pytest_asyncio.fixture(name="default_user", scope="function")
async def fixture_default_user(session: AsyncSession) -> User:
    return await get_or_create_default_user(session)


@pytest.fixture(name="default_user_headers", scope="function")
def fixture_default_user_headers(default_user: User) -> dict[str, str]:
    access_token = JWTProvider.create_access_token(default_user.id, default_user.rstr)
    return {"Authorization": f"Bearer {access_token}"}
