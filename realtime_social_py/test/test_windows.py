# tests/test_windows.py
import asyncio
from app.windows import tumbling
from collections import deque

async def feed(q):
    for ts in range(10):
        await q.put({"ts": ts, "tags": ["#a"]})

async def test_tumbling_batches():
    q = asyncio.Queue()
    asyncio.create_task(feed(q))
    agen = tumbling(q, window_sec=0.01)
    batch1 = await agen.__anext__()
    assert "items" in batch1
