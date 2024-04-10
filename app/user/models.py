from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.db.models_mixin import TimestampMixin
from core.db.session import Base


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(127), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_super_admin: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(512), default=None, nullable=True)
    rstr: Mapped[str] = mapped_column(String(31), nullable=False)
    last_login: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
