# app/stream.py
import asyncio, random, re, time
HASHTAG_RE = re.compile(r"#\w+", re.UNICODE)

async def simulated_stream(rate_hz: float = 20.0):
    """Generador asíncrono: emite ~rate_hz posts/seg (procesamiento perezoso)."""
    dt = 1.0 / rate_hz
    tags = ["#ai", "#python", "#java", "#nlp", "#efficient", "#stream"]
    while True:
        yield {"ts": time.time(), "text": f"Post {random.randint(1,999)} {random.choice(tags)}"}
        await asyncio.sleep(dt)

def extract_hashtags(text: str) -> list[str]:
    return [h.lower() for h in HASHTAG_RE.findall(text)]
