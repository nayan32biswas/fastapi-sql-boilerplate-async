from datetime import datetime, timedelta
from secrets import token_hex

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from app.user.models import ForgotPassword, User
from app.user.models_manager.user import UserManager
from app.user.schemas.auth import (
    ForgotPasswordRequestIn,
    ForgotPasswordResetIn,
    LoginIn,
    PasswordChangeIn,
    RefreshTokenIn,
    RegistrationIn,
)
from core import constants
from core.auth import PasswordUtils
from core.auth.jwt import JWTProvider
from core.config import settings
from core.deps.auth import CurrentUser
from core.deps.db import CurrentAsyncSession
from core.utils.string import generate_rstr
from worker.tasks.email import send_email

router = APIRouter(
    prefix="/auth",
)


@router.post("/registration", status_code=status.HTTP_201_CREATED)
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


@router.post("/swagger-login")
async def swagger_login(
    session: CurrentAsyncSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await handle_login(session, form_data.username, form_data.password)


@router.post("/login")
async def token_login(
    data: LoginIn,
    session: CurrentAsyncSession,
):
    token = await handle_login(session, data.email, data.password)

    return token


@router.post("/refresh-token")
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


@router.post("/change-password")
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


@router.post("/forgot-password-request")
async def forgot_password_request(
    session: CurrentAsyncSession,
    data: ForgotPasswordRequestIn,
):
    email = data.email

    user_manager = UserManager(session)

    user: User = await user_manager.get_obj_or_404(email=email)

    expire_at = datetime.now() + timedelta(minutes=constants.FORGOT_PASSWORD_EXPIRE_MINUTES)

    forgot_password_instance = ForgotPassword(
        user_id=user.id,
        email=data.email,
        expire_at=expire_at,
        token=token_hex(60),
    )
    session.add(forgot_password_instance)
    await session.commit()

    forgot_password_url = f"{settings.API_HOST}/{constants.FORGOT_PASSWORD_PATH}?token={forgot_password_instance.token}"

    send_email.delay(
        to=[user.email],
        subject="Forgot password request",
        data={
            "url": forgot_password_url,
        },
    )

    return {"message": "Check your email inbox to set new password"}


@router.post("/forgot-password-reset")
async def forgot_password_reset(
    session: CurrentAsyncSession,
    data: ForgotPasswordResetIn,
):
    stmt = (
        sa.select(ForgotPassword)
        .where(ForgotPassword.token == data.token)
        .options(joinedload(ForgotPassword.user))
    )
    result = await session.execute(stmt)
    forgot_password_instance = result.scalars().first()
    user = forgot_password_instance.user

    if forgot_password_instance.is_used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")

    if forgot_password_instance.expire_at < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is expired")

    forgot_password_instance.is_used = True
    forgot_password_instance.used_at = datetime.now()

    user.hashed_password = PasswordUtils.get_hashed_password(data.new_password)

    if data.force_logout is True:
        user.rstr = generate_rstr(31)

    await session.commit()

    send_email.delay(to=[user.email], subject="New password set")

    return {"message": "Successfully reset password"}
