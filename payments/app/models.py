import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import HttpUrl
from sqlalchemy import BigInteger, DateTime, Numeric, String, TypeDecorator, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func, text

from app.enums import State


class HttpUrlType(TypeDecorator):
    impl = String(2083)
    cache_ok = True
    python_type = HttpUrl

    def process_bind_param(self, value, dialect) -> str:
        return str(value)

    def process_literal_param(self, value, dialect) -> str:
        return str(value)

    def process_result_value(self, value, dialect) -> HttpUrl:
        return HttpUrl(url=value)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        default=uuid.uuid7,
        server_default=text("uuidv7()"),
        unique=True,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    currency: Mapped[str] = mapped_column(String(3))
    description: Mapped[str] = mapped_column(String(256))
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    state: Mapped[State] = mapped_column(String(10), server_default=text("'pending'"))
    webhook_url: Mapped[HttpUrl] = mapped_column(HttpUrlType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class OutboxEvent(Base):
    __tablename__ = "outbox"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    aggregatetype: Mapped[str] = mapped_column(String(255))
    aggregateid: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
