import asyncio
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from random import choices, randint

from app.cache import CacheError, cache
from app.database import DBError, pool
from app.enums import Currency, State
from app.webhook import WebhookError, WebhookHandler

_PENDING_TTL = 30
_PROCESSED_TTL = 86400

_STATE_UPDATE = """
    UPDATE payments
    SET state=$1, processed_at=NOW()
    WHERE public_id=$2
"""


class PaymentError(Exception): ...


class ProcessingError(PaymentError):
    def __init__(self, msg="Experienced error during processing"):
        super().__init__(msg)


class PersistenceError(PaymentError):
    def __init__(self, msg="Data write error"):
        super().__init__(msg)


class DeduplicationError(PaymentError):
    def __init__(self, msg="Can't provide deduplication"):
        super().__init__(msg)


@dataclass
class Payment:
    amount: Decimal
    currency: Currency
    description: str
    webhook_url: str
    public_id: str
    state: State
    created_at: datetime
    meta: str | None = None

    def __post_init__(self):
        self.webhook_url = str(self.webhook_url)
        self.public_id = str(self.public_id)

    @staticmethod
    async def _emulate_processing():
        await asyncio.sleep(randint(2, 5))
        if not choices((True, False), weights=(0.9, 0.1))[0]:
            raise ProcessingError()

    async def _db_state(self, state: State):
        await pool.query(_STATE_UPDATE, state, self.public_id)

    async def _safe_db_state(self, state: State):
        await pool.safe_query(_STATE_UPDATE, state, self.public_id)

    async def _cache_state(self, state: State):
        await cache.set(self.public_id, state, _PROCESSED_TTL)

    async def set_succeeded(self):
        try:
            await self._db_state(State.SUCCEEDED)
        except DBError:
            raise PersistenceError()
        await self._cache_state(State.SUCCEEDED)

    async def set_failed(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._safe_db_state(State.FAILED))
            tg.create_task(self._cache_state(State.FAILED))

    async def allowed(self):
        try:
            return await cache.set_atomic(self.public_id, self.state, _PENDING_TTL)
        except CacheError:
            raise DeduplicationError()

    async def process(self):
        await self._emulate_processing()  # Must be revertable! Other way what's a point?
        await self.set_succeeded()

    async def post_process(self):
        try:
            await WebhookHandler(url=self.webhook_url, timeout=5.0).execute()
        except WebhookError:
            pass  # Do something
