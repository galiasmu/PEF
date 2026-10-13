"""Tests del servidor: integración de punta a punta y reparto a los clientes."""
import asyncio

from fastapi.testclient import TestClient

from app import main
from app.config import settings
from app.sentiment import lexicon_scores


def lexicon_model(model_name):
    """Reemplazo del modelo en los tests: análisis léxico, sin descargar nada."""
    return lambda texts: [lexicon_scores(t) for t in texts]


def test_end_to_end_with_simulated_source(monkeypatch):
    """Servidor + pipeline + fuente simulada + WebSocket, sin API key ni modelo pesado."""
    monkeypatch.setattr(settings, "source", "simulated")
    monkeypatch.setattr(settings, "poll_interval_seconds", 0.05)
    monkeypatch.setattr(settings, "window_seconds", 0.2)
    monkeypatch.setattr(main, "load_model", lexicon_model)

    with TestClient(main.app) as client, client.websocket_connect("/ws/metrics") as ws:
        summaries = [ws.receive_json() for _ in range(3)]

    keys = {"total_comments", "top_hashtags", "trending", "avg_sentiment"}
    assert all(set(summary) == keys for summary in summaries)
    assert sum(summary["total_comments"] for summary in summaries) > 0


class FakeClient:
    """Cliente WebSocket falso: guarda lo que recibe, o falla si está 'caído'."""

    def __init__(self, broken=False):
        self.broken = broken
        self.received = []

    async def send_json(self, message):
        if self.broken:
            raise ConnectionError("cliente caído")
        self.received.append(message)


async def test_broadcast_sends_to_all_and_drops_broken_clients(monkeypatch):
    ok, broken = FakeClient(), FakeClient(broken=True)
    monkeypatch.setattr(main, "clients", {ok, broken})

    await main.broadcast({"total_comments": 1})

    assert ok.received == [{"total_comments": 1}]
    assert main.clients == {ok}       # el cliente caído se descartó


async def test_background_task_errors_are_logged(caplog):
    async def failing_task():
        raise ValueError("la API cambió de formato")

    task = asyncio.create_task(failing_task(), name="productor")
    task.add_done_callback(main.log_task_error)
    await asyncio.gather(task, return_exceptions=True)
    await asyncio.sleep(0)  # deja correr el callback

    assert "La tarea productor se detuvo por un error" in caplog.text
    assert "la API cambió de formato" in caplog.text
