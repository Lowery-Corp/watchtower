import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class LoginLog(Base):
    __tablename__ = "login_log"

    __table_args__ = (
        Index("ix_login_log_user_id", "user_id"),
        Index("ix_login_log_datetime", "login_datetime"),
        {"schema": "app"},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    login_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )