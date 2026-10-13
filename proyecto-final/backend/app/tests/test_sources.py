from app.sources import SeenIds, parse_comment, simulated_comments


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
    item = {"id": "abc", "snippet": {"topLevelComment": {"snippet": {"textOriginal": "hola #ia"}}}}
    assert parse_comment(item) == {"id": "abc", "text": "hola #ia"}


async def test_simulated_batches():
    source = simulated_comments(max_per_batch=5, interval=0, seed=1)
    batches = [await anext(source) for _ in range(3)]
    await source.aclose()

    ids = [c["id"] for batch in batches for c in batch]
    assert all(len(batch) <= 5 for batch in batches)
    assert len(ids) == len(set(ids))  # cada comentario tiene un ID único
