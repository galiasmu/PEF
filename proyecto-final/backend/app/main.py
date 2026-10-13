# backend/app/main.py
import asyncio
import re
from collections import Counter
from contextlib import aclosing

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from .config import settings
from .pipeline import produce, time_windows
from .sources import build_source

# ----------------- Configuración -----------------
# Con la fuente de YouTube, el servidor no arranca si falta la API key.
if settings.source == "youtube":
    settings.require_youtube()

# --------------- Sentimiento ---------------
def build_sentiment():
    try:
        from transformers import pipeline
        model = settings.model_name
        pipe = pipeline("text-classification", model=model, tokenizer=model, top_k=None)
        def _f(text: str):
            if not text:
                return {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
            res = pipe(text, truncation=True)[0]
            out = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
            for it in res:
                lab = it["label"].lower()
                if "pos" in lab: out["positive"] = float(it["score"])
                elif "neu" in lab: out["neutral"] = float(it["score"])
                elif "neg" in lab or "label_0" in lab: out["negative"] = float(it["score"])
            if out["positive"] == out["neutral"] == out["negative"] == 0.0:
                out["neutral"] = 1.0
            return out
        return _f
    except Exception:
        pos = {"genial","buena","excelente","increible","bien","me encanta","gracias","love","cool"}
        neg = {"malo","horrible","odio","asco","mierda","wtf","feo"}
        def _f(text: str):
            t = (text or "").lower()
            p = sum(w in t for w in pos)
            n = sum(w in t for w in neg)
            if p == 0 and n == 0: return {"positive":0.0,"neutral":1.0,"negative":0.0}
            tot = p + n
            return {"positive": p/tot, "neutral": 0.0, "negative": n/tot}
        return _f

analyze_sentiment = build_sentiment()

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
    async with aclosing(build_source()) as source:
        producer = asyncio.create_task(produce(source, queue))
        try:
            async for window in time_windows(queue, settings.window_seconds):
                for comment in window:
                    comment["sentiment"] = analyze_sentiment(comment["text"])
                await ws.send_json(aggregate(window))
        finally:
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)

def aggregate(batch):
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

    n = max(total, 1)
    return {
        "total_comments": total,
        "top_hashtags": tags.most_common(10),
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
