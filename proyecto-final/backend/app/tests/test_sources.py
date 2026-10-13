from aiohttp import web
from aiohttp.test_utils import TestServer

from app import sources
from app.sources import SeenIds, parse_comment, simulated_comments, youtube_comments

API_ITEM = {"id": "c1", "snippet": {"topLevelComment": {"snippet": {"textOriginal": "hola #ia"}}}}


def test_seen_ids_dedupe():
    seen = SeenIds()
    assert seen.add("a") is True
    assert seen.add("a") is False


def test_seen_ids_bounded_memory():
    seen = SeenIds(maxlen=3)
    for i in range(10):
        seen.add(str(i))
    assert len(seen) == 3            # nunca guarda más de maxlen IDs
    assert seen.add("9") is False    # reciente: lo sigue recordando
    assert seen.add("0") is True     # viejo: ya lo olvidó


def test_parse_comment():
    assert parse_comment(API_ITEM) == {"id": "c1", "text": "hola #ia"}


async def test_youtube_comments_with_fake_api(monkeypatch):
    """Un servidor falso imita a la API de YouTube: 2 respuestas iguales y un error de cuota."""
    responses = [web.json_response({"items": [API_ITEM]}),
                 web.json_response({"items": [API_ITEM]}),
                 web.Response(status=403)]

    async def fake_api(request):
        return responses.pop(0)

    app = web.Application()
    app.router.add_get("/", fake_api)
    async with TestServer(app) as server:
        monkeypatch.setattr(sources, "API_URL", str(server.make_url("/")))
        stream = youtube_comments("clave", "video", "abc", poll_interval=0)

        assert await anext(stream) == [{"id": "c1", "text": "hola #ia"}]
        assert await anext(stream) == []    # el mismo comentario otra vez: ya visto
        assert await anext(stream) == []    # error 403 (cuota agotada): lote vacío y sigue
        await stream.aclose()


async def test_simulated_batches():
    source = simulated_comments(max_per_batch=5, interval=0, seed=1)
    batches = [await anext(source) for _ in range(3)]
    await source.aclose()

    ids = [c["id"] for batch in batches for c in batch]
    assert all(len(batch) <= 5 for batch in batches)
    assert len(ids) == len(set(ids))  # cada comentario tiene un ID único
