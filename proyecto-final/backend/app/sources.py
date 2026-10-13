"""Fuentes de datos: de dónde salen los comentarios.

Cada fuente es un generador asíncrono que, en cada iteración, entrega un
lote (lista) con los comentarios nuevos. Así el stream se procesa de a
partes, sin cargarlo entero en memoria y sin bloquear el event loop.

- youtube_comments: comentarios reales de la YouTube Data API v3.
- simulated_comments: comentarios falsos, para probar sin API key.
"""
import asyncio
import itertools
import logging
import random
from collections import deque
from collections.abc import AsyncIterator

import aiohttp

from .config import settings

log = logging.getLogger(__name__)

API_URL = "https://www.googleapis.com/youtube/v3/commentThreads"


class SeenIds:
    """Recuerda los últimos IDs vistos usando memoria acotada.

    El set permite saber en O(1) si un ID ya se vio, y la deque guarda el
    orden de llegada para olvidar el más viejo cuando se supera ``maxlen``.
    """

    def __init__(self, maxlen: int = 10_000):
        self.maxlen = maxlen
        self._ids: set[str] = set()
        self._order: deque[str] = deque()

    def add(self, item_id: str) -> bool:
        """Registra un ID. Devuelve False si ya se había visto."""
        if item_id in self._ids:
            return False
        self._ids.add(item_id)
        self._order.append(item_id)
        if len(self._order) > self.maxlen:
            self._ids.remove(self._order.popleft())
        return True

    def __len__(self) -> int:
        return len(self._ids)


def parse_comment(item: dict) -> dict:
    """Toma un ``commentThread`` de la API y se queda solo con lo que usamos."""
    snippet = item["snippet"]["topLevelComment"]["snippet"]
    return {"id": item["id"], "text": snippet.get("textOriginal", "")}


async def youtube_comments(api_key: str, target_type: str, target_id: str,
                           poll_interval: float) -> AsyncIterator[list[dict]]:
    """Consulta YouTube cada ``poll_interval`` segundos y entrega los comentarios nuevos.

    Pide siempre los 100 más recientes (``order=time``) y descarta los que ya
    se vieron. Si la consulta falla (red caída, cuota de la API agotada),
    entrega un lote vacío y vuelve a intentar en la próxima vuelta.
    """
    params = {"part": "snippet", "order": "time", "maxResults": "100", "key": api_key}
    if target_type == "channel":
        params["allThreadsRelatedToChannelId"] = target_id
    else:
        params["videoId"] = target_id

    seen = SeenIds()
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            try:
                async with session.get(API_URL, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                comments = [parse_comment(item) for item in data.get("items", [])]
                new_comments = [c for c in comments if seen.add(c["id"])]
            # Se loguea solo el tipo de error: el error completo incluye la URL con la API key.
            except aiohttp.ClientResponseError as e:
                log.warning("YouTube respondió %s (%s)", e.status, e.message)
                new_comments = []
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                log.warning("No se pudo consultar YouTube: %s", type(e).__name__)
                new_comments = []
            yield new_comments
            await asyncio.sleep(poll_interval)


PHRASES = [
    "me encanta este video",
    "excelente explicación, gracias",
    "muy buena la edición",
    "primera vez que veo el canal",
    "no me gustó nada",
    "horrible el audio",
    "odio cuando cortan así",
]
HASHTAGS = ["#python", "#ia", "#eficiencia", "#streaming", "#datos"]


def fake_comment(rnd: random.Random, comment_id: int) -> dict:
    """Arma un comentario falso: una frase y hasta dos hashtags."""
    tags = rnd.sample(HASHTAGS, k=rnd.randint(0, 2))
    return {"id": f"sim-{comment_id}", "text": " ".join([rnd.choice(PHRASES), *tags])}


async def simulated_comments(max_per_batch: int = 20, interval: float = 1.0,
                             seed: int | None = None) -> AsyncIterator[list[dict]]:
    """Entrega cada ``interval`` segundos un lote de 0 a ``max_per_batch`` comentarios falsos.

    Con ``seed`` la secuencia es siempre la misma (útil para tests y mediciones).
    """
    rnd = random.Random(seed)
    ids = itertools.count(1)
    while True:
        yield [fake_comment(rnd, next(ids)) for _ in range(rnd.randint(0, max_per_batch))]
        await asyncio.sleep(interval)


def build_source() -> AsyncIterator[list[dict]]:
    """Devuelve la fuente elegida en la configuración (``SOURCE``)."""
    if settings.source == "simulated":
        return simulated_comments(interval=settings.poll_interval_seconds)
    return youtube_comments(settings.youtube_api_key, settings.target_type,
                            settings.target_id, settings.poll_interval_seconds)
