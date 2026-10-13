# backend/app/main.py
import asyncio
import re
import time
from collections import Counter

import requests
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from .config import settings

# ----------------- Configuración -----------------
settings.require_youtube()

API_KEY = settings.youtube_api_key
TARGET_TYPE = settings.target_type
VIDEO_ID = settings.target_id
POLL_INTERVAL = settings.poll_interval_seconds
WINDOW_SECONDS = settings.window_seconds
MODEL_NAME = settings.model_name

# --------------- Sentimiento ---------------
def build_sentiment():
    try:
        from transformers import pipeline
        pipe = pipeline("text-classification", model=MODEL_NAME, tokenizer=MODEL_NAME, top_k=None)
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
    return {"status": "ok", "video_id": VIDEO_ID}

# ----------- Colector + Ventanas -----------
async def collect_and_window(ws: WebSocket):
    """
    Bucle que:
      - hace poll a commentThreads orden=time (máx 50)
      - acumula nuevos comments en buffer
      - cada WINDOW_SECONDS envía payload agregado al WS (aunque esté vacío)
    """
    seen = set()
    buffer = []
    last_flush = time.monotonic()

    while True:
        # 1) poll youtube
        try:
            params = {
                "part": "snippet",
                "order": "time",
                "maxResults": 50,
                "videoId": VIDEO_ID,
                "key": API_KEY,
            }
            r = requests.get(
                "https://www.googleapis.com/youtube/v3/commentThreads",
                params=params, timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                for it in data.get("items", []):
                    top = it.get("snippet", {}).get("topLevelComment", {})
                    sn = top.get("snippet", {})
                    cid = top.get("id") or it.get("id")
                    if not cid or cid in seen:
                        continue
                    seen.add(cid)
                    text = sn.get("textOriginal") or sn.get("textDisplay") or ""
                    sent = analyze_sentiment(text)
                    buffer.append({
                        "id": cid,
                        "text": text,
                        "sentiment": sent
                    })
            else:
                print("YouTube API error:", r.status_code, r.text[:200])
        except Exception as e:
            print("poll error:", repr(e))

        # 2) flush de ventana cada WINDOW_SECONDS
        now = time.monotonic()
        if now - last_flush >= WINDOW_SECONDS:
            payload = aggregate(buffer)
            try:
                await ws.send_json(payload)
            except WebSocketDisconnect:
                print("WS cliente desconectado")
                break
            except Exception as e:
                print("WS send error:", repr(e))
                break
            buffer.clear()
            last_flush = now

        await asyncio.sleep(POLL_INTERVAL)

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
