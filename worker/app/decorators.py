import asyncio
from collections.abc import Callable
from functools import wraps
from random import random


def retry(
    max_retries: int,
    backoff_factor: float = 2.0,
    use_jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    await func(*args, **kwargs)
                    return
                except exceptions:
                    jitter = random() if use_jitter else 0
                    cooldown_time = backoff_factor**attempt + jitter
                    await asyncio.sleep(cooldown_time)

        return wrapper

    return decorator
