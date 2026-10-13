import asyncio
import pytest
from app.windows import time_window

async def gen():
    for i in range(5):
        yield {"i": i}

@pytest.mark.asyncio
async def test_windows():
    out = []
    async for b in time_window(gen(), 0):
        out.append(b)
    assert sum(len(x) for x in out) == 5
