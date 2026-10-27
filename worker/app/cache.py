from contextlib import suppress

import redis.asyncio as aioredis
from redis.typing import EncodableT

from app.settings import settings


class CacheError(Exception):
    def __init__(self, msg="Cache error"):
        super().__init__(msg)


class _Cache:
    def __init__(self):
        self.redis = None

    def create(self):
        self.redis = aioredis.from_url(settings.redis_url, db=1, decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set_atomic(self, key: str, value: EncodableT, expired: int = 30) -> bool:
        try:
            return await self.redis.set(key, value, ex=expired, nx=True)
        except aioredis.RedisError:
            raise CacheError()

    async def set(self, key: str, value: EncodableT, expired: int = 86400):
        with suppress(aioredis.RedisError):
            await self.redis.set(key, value, ex=expired)


cache = _Cache()
