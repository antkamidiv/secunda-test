import asyncio
from contextlib import suppress

import asyncpg

from app.settings import settings

_CONNECTION_TIMEOUT = 5.0
_GRACEFULLY_SHUTDOWN_TIMEOUT = 5.0


_AsyncpgExceptions = (asyncpg.PostgresError, asyncpg.InterfaceError, asyncpg.InternalClientError)


class DBError(Exception):
    def __init__(self, msg="Database error"):
        super().__init__(msg)


class _DatabasePool:
    def __init__(self):
        self.pool = None

    async def create(self):
        try:
            self.pool = await asyncpg.create_pool(settings.postgresql_url)
        except _AsyncpgExceptions:
            raise DBError()

    async def close(self):
        if self.pool:
            try:
                await asyncio.wait_for(self.pool.close(), timeout=_GRACEFULLY_SHUTDOWN_TIMEOUT)
            except TimeoutError:
                self.pool.terminate()

    async def query(self, query: str, *args):
        try:
            async with self.pool.acquire(timeout=_CONNECTION_TIMEOUT) as conn:
                await conn.execute(query, *args)
        except _AsyncpgExceptions:
            raise DBError()

    async def safe_query(self, query: str, *args):
        with suppress(DBError):
            await self.query(query, *args)


pool = _DatabasePool()
