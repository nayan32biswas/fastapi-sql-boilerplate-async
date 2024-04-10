from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select

from app.user.models import User
from core.auth.jwt import JWTProvider, TokenData

from .db import AsyncSession, CurrentAsyncSession

tokenUrl = "api/v1/auth/swagger-login"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=tokenUrl,
    auto_error=False,
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)


async def get_user(session: AsyncSession, token_data: TokenData) -> Optional[User]:
    stmt = await session.execute(select(User).where(User.id == token_data.id))

    return stmt.scalars().first()


async def get_authenticated_token(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        raise credentials_exception

    return JWTProvider.decode_access_token(token)


async def get_authenticated_token_or_none(token: Optional[str] = Depends(oauth2_scheme)):
    if token is None:
        return None

    return JWTProvider.decode_access_token(token)


async def get_authenticated_user(
    session: CurrentAsyncSession,
    token_data: Annotated[TokenData, Depends(get_authenticated_token)],
) -> User:
    user = await get_user(session, token_data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_authenticated_user_or_none(
    session: CurrentAsyncSession,
    token_data: Annotated[Optional[TokenData], Depends(get_authenticated_token)],
) -> Optional[User]:
    if not token_data:
        return None

    user = await get_user(session, token_data)

    return user


AuthenticatedTokenData = Annotated[TokenData, Depends(get_authenticated_token)]
AuthenticatedTokenDataOrNone = Annotated[
    Optional[TokenData], Depends(get_authenticated_token_or_none)
]

CurrentUser = Annotated[User, Depends(get_authenticated_user)]
CurrentUserOrNone = Annotated[Optional[User], Depends(get_authenticated_user_or_none)]
