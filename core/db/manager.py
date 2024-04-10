from typing import Optional, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta

T = TypeVar("T")


class BaseManager:
    def __init__(self, db: AsyncSession, model: DeclarativeMeta) -> None:
        self.db = db
        self.model = model

    async def get_first(self, **kwargs) -> Optional[T]:
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.db.execute(stmt)
        obj = result.scalars().first()

        return obj

    async def get_obj_or_404(self, **kwargs) -> T:
        obj = await self.get_first(**kwargs)

        if not obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Object not found")

        return obj
