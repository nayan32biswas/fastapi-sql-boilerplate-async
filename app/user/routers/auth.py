from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.user.models import User
from app.user.models_manager.user import UserManager
from app.user.schemas.auth import (
    ForgotPasswordRequestIn,
    LoginIn,
    PasswordChangeIn,
    RefreshTokenIn,
    RegistrationIn,
)
from core.auth import PasswordUtils
from core.auth.jwt import JWTProvider
from core.deps.auth import CurrentUser
from core.deps.db import CurrentAsyncSession
from core.utils.string import generate_rstr
from worker.tasks.email import send_email

auth_router = APIRouter()


@auth_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    data: RegistrationIn,
    session: CurrentAsyncSession,
):
    user_manager = UserManager(session)
    user = await user_manager.get_user_by_email(data.email)

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exists")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=PasswordUtils.get_hashed_password(data.password),
        is_active=True,
        rstr=generate_rstr(31),
    )

    user_manager = UserManager(session)

    await user_manager.create(user)

    return {"message": "User created"}


async def handle_login(session: AsyncSession, email: str, password: str):
    user_manager = UserManager(session)

    user = await user_manager.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if not PasswordUtils.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")
    refresh_token = JWTProvider.create_refresh_token(id=user.id, rstr="temp")

    user.last_login = datetime.now()
    await session.commit()

    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/swagger-login")
async def swagger_login(
    session: CurrentAsyncSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await handle_login(session, form_data.username, form_data.password)


@auth_router.post("/login")
async def token_login(
    data: LoginIn,
    session: CurrentAsyncSession,
):
    token = await handle_login(session, data.email, data.password)

    return token


@auth_router.post("/refresh-token")
async def refresh_token(
    session: CurrentAsyncSession,
    data: RefreshTokenIn,
):
    refresh_token_payload = JWTProvider.decode_refresh_token(data.refresh_token)

    user_manager = UserManager(session)

    user = await user_manager.get_user_by_id(refresh_token_payload.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token or user is not active",
        )

    access_token = JWTProvider.create_access_token(id=user.id, rstr="temp")

    return {"access_token": access_token}


@auth_router.post("/change-password")
async def change_password(
    user: CurrentUser,
    session: CurrentAsyncSession,
    data: PasswordChangeIn,
):
    old_password = data.old_password
    new_password = data.new_password

    if not PasswordUtils.verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    user.hashed_password = PasswordUtils.get_hashed_password(new_password)
    await session.commit()

    return {"message": "Successfully change the password"}


@auth_router.post("/forgot-password-request")
async def forgot_password_request(
    session: CurrentAsyncSession,
    data: ForgotPasswordRequestIn,
):
    email = data.email

    user_manager = UserManager(session)

    user: User = await user_manager.get_obj_or_404(email=email)

    send_email.delay(to=[user.email], subject="Forgot password request")

    return {"message": "Check your email inbox to set new password"}
