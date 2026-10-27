from collections.abc import Generator
from contextlib import contextmanager

import aiohttp
from aiohttp.client import DEFAULT_TIMEOUT

from app.decorators import retry


class WebhookError(Exception):
    def __init__(self, msg: str = "Failed request to webhook server"):
        super().__init__(msg)


class _WebhookSessionManager:
    _session = None

    async def close(self):
        if self._session:
            await self._session.close()

    @contextmanager
    def session(self) -> Generator[aiohttp.ClientSession]:
        if not self._session:
            self._session = aiohttp.ClientSession()
        yield self._session


session_manager = _WebhookSessionManager()


class WebhookHandler:
    def __init__(self, url: str, timeout: float | None = None):
        self.url = url
        self.timeout = aiohttp.ClientTimeout(timeout) if timeout else DEFAULT_TIMEOUT

    @retry(max_retries=5, exceptions=(TimeoutError, aiohttp.ClientConnectionError))
    async def execute(self):
        with session_manager.session() as session:
            async with session.get(self.url, timeout=self.timeout) as response:
                if response.ok:  # Any other condition to confirm request's successful
                    return
        raise WebhookError()
