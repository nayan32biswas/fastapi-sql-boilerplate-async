import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict

import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


class TokenData(BaseModel):
    id: int
    rstr: str


invalid_token = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid Token",
)

invalid_access_token = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid Access Token",
)

invalid_refresh_token = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Invalid Refresh Token",
)


class JWTProvider:
    @classmethod
    def _create_token(cls, payload: Dict[str, Any], exp: timedelta) -> str:
        expire = datetime.now() + exp

        payload["exp"] = expire
        payload["iat"] = time.time()

        try:
            token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        except Exception as e:
            raise invalid_token from e

        return token

    @classmethod
    def create_access_token(cls, id: int, rstr: str) -> str:
        payload = {
            "id": id,
            "rstr": rstr,
            "token_type": TokenType.ACCESS,
        }

        return cls._create_token(payload, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    @classmethod
    def create_refresh_token(cls, id: int, rstr: str) -> str:
        payload = {
            "id": id,
            "rstr": rstr,
            "token_type": TokenType.REFRESH,
        }

        return cls._create_token(payload, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    @classmethod
    def _decode_token(cls, token: str) -> Dict[str, Any]:
        if not token:
            raise invalid_token

        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        if "token_type" not in payload:
            raise invalid_token

        return payload

    @classmethod
    def decode_access_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.ACCESS:
            raise invalid_access_token

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise invalid_access_token from e

    @classmethod
    def decode_refresh_token(cls, token: str):
        payload = cls._decode_token(token)

        if payload["token_type"] != TokenType.REFRESH:
            raise invalid_refresh_token

        try:
            return TokenData(id=payload["id"], rstr=payload["rstr"])
        except Exception as e:
            raise invalid_refresh_token from e
