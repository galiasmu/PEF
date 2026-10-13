# backend/app/main.py
import asyncio
import re
import time
from collections import Counter
from contextlib import aclosing

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from .config import settings
from .pipeline import produce, time_windows
from .sentiment import SentimentAnalyzer, load_model
from .sources import build_source
from .trends import TrendingHashtags

# ----------------- Configuración -----------------
# Con la fuente de YouTube, el servidor no arranca si falta la API key.
if settings.source == "youtube":
    settings.require_youtube()

# --------------- Sentimiento ---------------
analyzer = SentimentAnalyzer(load_model(settings.model_name))

HASHTAG_RE = re.compile(r"(#\w+)", re.UNICODE)
def extract_hashtags(text: str):
    return [h[1:].lower() for h in HASHTAG_RE.findall(text or "")]

# ----------------- FastAPI -----------------
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "source": settings.source, "target_id": settings.target_id}

# ----------- Colector + Ventanas -----------
async def collect_and_window(ws: WebSocket):
    """Arma el pipeline y envía al cliente el resumen de cada ventana.

        fuente ──► productor ──► cola (MAX_QUEUE) ──► ventanas ──► WebSocket

    El productor corre como una tarea aparte, así sigue trayendo comentarios
    mientras se procesa la ventana anterior. Al salir (por ejemplo, porque el
    cliente se desconectó) se cancela el productor y ``aclosing`` cierra la fuente.
    """
    queue = asyncio.Queue(maxsize=settings.max_queue)
    trends = TrendingHashtags(settings.trend_seconds)
    async with aclosing(build_source()) as source:
        producer = asyncio.create_task(produce(source, queue))
        try:
            async for window in time_windows(queue, settings.window_seconds):
                # El modelo corre en otro hilo: mientras analiza, el productor sigue trabajando.
                texts = [comment["text"] for comment in window]
                scores = await asyncio.to_thread(analyzer.analyze, texts)
                for comment, sentiment in zip(window, scores):
                    comment["sentiment"] = sentiment
                await ws.send_json(aggregate(window, trends))
        finally:
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)

def aggregate(batch, trends: TrendingHashtags):
    """Resume la ventana y actualiza las tendencias con sus hashtags."""
    total = len(batch)
    tags = Counter()
    sums = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}

    for b in batch:
        for h in extract_hashtags(b["text"]):
            tags[h] += 1
        s = b["sentiment"]
        sums["positive"] += float(s.get("positive", 0.0))
        sums["neutral"]  += float(s.get("neutral", 0.0))
        sums["negative"] += float(s.get("negative", 0.0))

    trends.add(tags, time.monotonic())

    n = max(total, 1)
    return {
        "total_comments": total,
        "top_hashtags": tags.most_common(10),
        "trending": trends.top(10),
        "avg_sentiment": {k: v/n for k, v in sums.items()},
    }

# ---------------- WebSocket ----------------
@app.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket):
    await ws.accept()
    print("✅ WS conectado")
    try:
        await collect_and_window(ws)
    except WebSocketDisconnect:
        print("🔌 WS cerrado por cliente")
    except Exception as e:
        print("💥 WS error:", repr(e))
    finally:
        try:
            await ws.close(code=1000)
        except Exception:
            pass
