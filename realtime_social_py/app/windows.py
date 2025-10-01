import asyncio, time
from typing import AsyncGenerator

async def tumbling(out_q: asyncio.Queue, window_sec=5) -> AsyncGenerator[dict, None]:
    bucket, t0 = [], time.time()
    while True:
        timeout = max(0.0, t0 + window_sec - time.time())
        try:
            item = await asyncio.wait_for(out_q.get(), timeout=timeout)
            bucket.append(item); out_q.task_done()
        except asyncio.TimeoutError:
            yield {"start": t0, "end": time.time(), "items": bucket}
            bucket, t0 = [], time.time()
