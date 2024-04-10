from fastapi import APIRouter

from app.user.schemas.user import UserMeOut
from core.deps.auth import CurrentUser

user_router = APIRouter()


@user_router.get("/me", response_model=UserMeOut)
async def get_me(
    user: CurrentUser,
):
    return UserMeOut.model_validate(user)
