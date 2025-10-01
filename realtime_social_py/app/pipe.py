# app/pipe.py
import asyncio
from .stream import simulated_stream, extract_hashtags

async def start_pipeline(n_workers=4):
    in_q, out_q = asyncio.Queue(10000), asyncio.Queue(10000)

    async def producer():
        async for post in simulated_stream():
            await in_q.put(post)

    async def worker():
        while True:
            post = await in_q.get()
            tags = extract_hashtags(post["text"])
            await out_q.put({"ts": post["ts"], "tags": tags})
            in_q.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(n_workers)]
    return producer, workers, in_q, out_q
