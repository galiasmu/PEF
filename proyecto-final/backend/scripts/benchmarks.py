"""Benchmarks: mide cada optimización del proyecto, comparando "antes" contra "después".

Uso (desde backend/):  python -m scripts.benchmarks
"""
import asyncio
import random
import time
import tracemalloc
from collections import Counter

from app.cache import LRUCache
from app.config import settings
from app.sentiment import SentimentAnalyzer, load_model
from app.sources import SeenIds, fake_comment
from app.trends import TrendingHashtags


def milliseconds(func, *args) -> float:
    """Cuántos milisegundos tarda en ejecutarse func(*args)."""
    start = time.perf_counter()
    func(*args)
    return (time.perf_counter() - start) * 1000


def megabytes(build) -> float:
    """Cuánta memoria (MB) ocupa la estructura que devuelve build()."""
    tracemalloc.start()
    structure = build()  # se mantiene viva mientras se mide
    used, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del structure
    return used / 1e6


def row(name: str, before: float, after: float, unit: str) -> None:
    print(f"| {name} | {before:,.2f} {unit} | {after:,.2f} {unit} | {before / after:,.0f}x |")


# --- 1. Cache: el TTLCache original (O(n)) contra el LRUCache (O(1)) -------------------

class OldTTLCache:
    """Cache original del proyecto: al llenarse busca el más viejo recorriendo todo (O(n))."""

    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.store = {}

    def put(self, key, value):
        if len(self.store) >= self.maxsize:
            oldest = min(self.store.items(), key=lambda item: item[1][0])[0]
            self.store.pop(oldest)
        self.store[key] = (time.time(), value)


def fill(cache, n: int = 10_000) -> None:
    for i in range(n):
        cache.put(i, i)


# --- 2. Comentarios ya vistos: set sin límite contra SeenIds (memoria acotada) ----------

def seen_set(n: int = 300_000) -> set:
    seen = set()
    for i in range(n):
        seen.add(f"comment-{i}")
    return seen


def seen_bounded(n: int = 300_000) -> SeenIds:
    seen = SeenIds(maxlen=10_000)
    for i in range(n):
        seen.add(f"comment-{i}")
    return seen


# --- 3. Tendencias: recalcular desde cero contra actualización incremental --------------

def fake_windows(n: int = 360) -> list[Counter]:
    """Una hora de ventanas de 10 s, cada una con hashtags al azar."""
    rnd = random.Random(1)
    return [Counter(rnd.choices([f"tag{i}" for i in range(50)], k=40)) for _ in range(n)]


def trends_from_scratch(windows: list[Counter]) -> None:
    history = []
    for i, counts in enumerate(windows):
        history.append((i * 10, counts))
        totals = Counter()
        for moment, old in history:  # cada ventana recorre toda la historia
            if i * 10 - moment <= 60:
                totals.update(old)
        totals.most_common(10)


def trends_incremental(windows: list[Counter]) -> None:
    trends = TrendingHashtags(seconds=60)
    for i, counts in enumerate(windows):
        trends.add(counts, i * 10)  # solo suma la nueva y descuenta las vencidas
        trends.top(10)


# --- 4 y 5. Modelo de sentimiento: de a uno, por lote, memoización y en otro hilo -------

def fake_texts(n: int = 64) -> list[str]:
    rnd = random.Random(1)
    return [fake_comment(rnd, i)["text"] for i in range(n)]


def one_by_one(predict, texts):
    for text in texts:
        predict([text])


async def longest_pause(analyze, texts, in_thread: bool) -> float:
    """Pausa más larga del event loop (en milisegundos) mientras se analiza un lote.

    Un "latido" intenta correr cada 10 ms: si el event loop está bloqueado, no puede.
    """
    pauses = []

    async def heartbeat():
        last = time.perf_counter()
        while True:
            await asyncio.sleep(0.01)
            now = time.perf_counter()
            pauses.append(now - last)
            last = now

    beat = asyncio.create_task(heartbeat())
    await asyncio.sleep(0.05)
    if in_thread:
        await asyncio.to_thread(analyze, texts)  # después: el modelo corre en otro hilo
    else:
        analyze(texts)                           # antes: el modelo bloquea el event loop
    await asyncio.sleep(0.05)
    beat.cancel()
    return max(pauses) * 1000


def main() -> None:
    print("| Optimización | Antes | Después | Mejora |")
    print("|---|---|---|---|")
    row("Cache con 10.000 inserciones (TTLCache O(n) → LRUCache O(1))",
        milliseconds(fill, OldTTLCache(2_000)), milliseconds(fill, LRUCache(2_000)), "ms")
    row("Memoria para recordar 300.000 comentarios vistos (set → SeenIds)",
        megabytes(seen_set), megabytes(seen_bounded), "MB")
    windows = fake_windows()
    row("Tendencias durante 1 hora de ventanas (desde cero → incremental)",
        milliseconds(trends_from_scratch, windows), milliseconds(trends_incremental, windows),
        "ms")

    predict = load_model(settings.model_name)
    texts = fake_texts()
    predict(["calentamiento"])  # la primera llamada al modelo es más lenta
    row("Sentimiento de 64 comentarios (de a uno → por lote)",
        milliseconds(one_by_one, predict, texts), milliseconds(predict, texts), "ms")
    analyzer = SentimentAnalyzer(predict)
    analyzer.analyze(texts)
    row("Sentimiento de 64 comentarios ya vistos (por lote → con memoización)",
        milliseconds(predict, texts), milliseconds(analyzer.analyze, texts), "ms")
    row("Pausa máxima del servidor mientras analiza (en el loop → en otro hilo)",
        asyncio.run(longest_pause(predict, texts, in_thread=False)),
        asyncio.run(longest_pause(predict, texts, in_thread=True)), "ms")


if __name__ == "__main__":
    main()
