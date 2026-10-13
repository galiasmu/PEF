import asyncio

from app.pipeline import produce, time_windows


async def fake_source():
    yield [{"id": "a"}, {"id": "b"}]
    yield []
    yield [{"id": "c"}]


async def test_produce_puts_every_comment():
    queue = asyncio.Queue()
    await produce(fake_source(), queue)
    assert [queue.get_nowait()["id"] for _ in range(queue.qsize())] == ["a", "b", "c"]


async def test_backpressure():
    queue = asyncio.Queue(maxsize=2)
    producer = asyncio.create_task(produce(fake_source(), queue))
    await asyncio.sleep(0.05)
    assert queue.qsize() == 2          # la cola nunca pasa su tamaño máximo
    assert not producer.done()         # el productor quedó esperando lugar
    producer.cancel()


async def test_time_windows_groups_and_emits_empty():
    queue = asyncio.Queue()
    for i in range(3):
        queue.put_nowait({"id": i})
    windows = time_windows(queue, seconds=0.05)

    assert len(await anext(windows)) == 3   # los 3 que estaban en la cola
    assert await anext(windows) == []       # sin datos: ventana vacía igual
