"""Servidor: arma el pipeline una sola vez y reparte cada resumen a todos los clientes.

    fuente ──► productor ──► cola ──► ventanas ──► sentimiento ──► resumen ──► clientes

El pipeline arranca junto con el servidor (``lifespan``) y es único: no
importa cuántas pestañas del dashboard estén abiertas, se consulta a YouTube
y se usa el modelo una sola vez por ventana.
"""
import asyncio
import logging
from contextlib import aclosing, asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .aggregator import summarize
from .config import settings
from .pipeline import produce, time_windows
from .sentiment import SentimentAnalyzer, load_model
from .sources import build_source
from .trends import TrendingHashtags

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")
log = logging.getLogger(__name__)

clients: set[WebSocket] = set()  # clientes conectados al WebSocket


async def broadcast(message: dict) -> None:
    """Envía el resumen a todos los clientes; descarta los que ya no responden."""
    for ws in list(clients):
        try:
            await ws.send_json(message)
        except Exception:
            clients.discard(ws)


async def run_pipeline(analyzer: SentimentAnalyzer) -> None:
    """Procesa el stream de comentarios ventana por ventana, mientras el servidor esté vivo.

    El productor corre como una tarea aparte, así sigue trayendo comentarios
    mientras se analiza la ventana anterior. El modelo corre en otro hilo
    (``asyncio.to_thread``) para no frenar al resto.
    """
    queue = asyncio.Queue(maxsize=settings.max_queue)
    trends = TrendingHashtags(settings.trend_seconds)
    async with aclosing(build_source()) as source:
        producer = asyncio.create_task(produce(source, queue))
        try:
            async for window in time_windows(queue, settings.window_seconds):
                texts = [comment["text"] for comment in window]
                scores = await asyncio.to_thread(analyzer.analyze, texts)
                for comment, sentiment in zip(window, scores):
                    comment["sentiment"] = sentiment
                await broadcast(summarize(window, trends))
        finally:
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Al arrancar el servidor, lanza el pipeline; al apagarlo, lo cancela."""
    if settings.source == "youtube":
        settings.require_youtube()  # sin API key, el servidor no arranca
    analyzer = SentimentAnalyzer(load_model(settings.model_name))
    log.info("Pipeline iniciado (fuente: %s)", settings.source)
    pipeline_task = asyncio.create_task(run_pipeline(analyzer))
    yield
    pipeline_task.cancel()
    await asyncio.gather(pipeline_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "source": settings.source, "clients": len(clients)}


@app.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket) -> None:
    """Registra al cliente: desde ahí recibe un resumen por cada ventana."""
    await ws.accept()
    clients.add(ws)
    log.info("Cliente conectado (%d en total)", len(clients))
    try:
        while True:
            await ws.receive_text()  # el cliente no envía nada: solo esperamos a que se vaya
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)
        log.info("Cliente desconectado (%d en total)", len(clients))
