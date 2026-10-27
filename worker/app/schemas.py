from datetime import datetime
from decimal import Decimal

from pydantic import UUID7, BaseModel, Field, HttpUrl, JsonValue

from app.enums import Currency, Queues, State


class PaymentModel(BaseModel):
    amount: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    currency: Currency
    description: str = Field(max_length=256)
    meta: JsonValue = None
    webhook_url: HttpUrl
    public_id: UUID7
    state: State
    created_at: datetime
    retry_queue: Queues | None = None

    @property
    def exhausted(self):
        return self.retry_queue == Queues.STAGE_3
