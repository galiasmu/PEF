# app/run.py
import asyncio, statistics as stats
from .pipe import start_pipeline
from .windows import tumbling
from .trends import TrendTopK
from .sentiment import score_text
import time

async def main():
    producer, workers, in_q, out_q = await start_pipeline()
    trends = TrendTopK(k=5, ttl_sec=60)
    asyncio.create_task(producer())

    async for batch in tumbling(out_q, window_sec=5):
        # actualizar tendencias + sentimiento
        scores = []
        for it in batch["items"]:
            trends.ingest(it["tags"], it["ts"])
            if it["tags"]:
                scores.append(score_text(" ".join(it["tags"])))
        trends.sweep(time.time())
        top = trends.topk()
        avg = round(stats.fmean(scores), 3) if scores else 0.0
        print(f"[{int(batch['start'])}-{int(batch['end'])}] top={top} sentiment_avg={avg}")

if __name__ == "__main__":
    asyncio.run(main())
