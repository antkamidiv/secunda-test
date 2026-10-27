from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid7

from pydantic import UUID7, BaseModel, ConfigDict, Field, HttpUrl, JsonValue

from app.enums import Currency, State


class PaymentCreateRequest(BaseModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: Currency
    description: str = Field(max_length=256)
    meta: JsonValue | None = None
    webhook_url: HttpUrl


class PaymentCreatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: UUID7 = Field(default_factory=uuid7)
    state: State = State.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PyamentDetailResponse(PaymentCreateRequest, PaymentCreatedResponse):
    model_config = ConfigDict(from_attributes=True)

    processed_at: datetime | None = None
