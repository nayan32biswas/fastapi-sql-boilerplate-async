from sqlalchemy.ext.asyncio.session import AsyncSession

from app.user.models import User
from core.db.manager import BaseManager


class UserManager(BaseManager):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db=db, model=User)

    async def create(self, user: User):
        self.db.add(user)

        await self.db.commit()

    async def get_user_by_id(self, id: int):
        user: User = await self.get_first(id=id)

        return user

    async def get_user_by_email(self, email: str):
        user: User = await self.get_first(email=email)

        return user
