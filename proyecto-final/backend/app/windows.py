import time
from typing import AsyncIterator, Dict, Any, List

async def time_window(aiter: AsyncIterator[Dict[str, Any]], window_seconds: int):
    """Agrupa elementos de un async iterator en ventanas de tiempo (tumbling)."""
    buf: List[Dict[str, Any]] = []
    window_start = time.monotonic()
    async for item in aiter:
        now = time.monotonic()
        if now - window_start >= window_seconds:
            yield buf
            buf = []
            window_start = now
        buf.append(item)
    if buf:
        yield buf
