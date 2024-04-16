from fastapi import APIRouter

from app.user.schemas.user import UserProfileIn, UserProfileOut
from core.deps.auth import CurrentUser
from core.deps.db import CurrentAsyncSession
from core.utils.model import update_model

router = APIRouter(prefix="/user")


@router.get("/profile", response_model=UserProfileOut)
async def get_profile(
    user: CurrentUser,
):
    return UserProfileOut.model_validate(user)


@router.put("/profile", response_model=UserProfileOut)
async def update_profile(
    user: CurrentUser,
    session: CurrentAsyncSession,
    data: UserProfileIn,
):
    user = update_model(user, data)
    await session.commit()

    await session.refresh(user)

    return UserProfileOut.model_validate(user)
