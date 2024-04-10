from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.db.session import get_async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_async_session() as session:
        yield session


CurrentAsyncSession = Annotated[AsyncSession, Depends(get_session)]
