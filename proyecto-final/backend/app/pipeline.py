"""Pipeline concurrente: productor ──► cola ──► ventanas de tiempo.

El productor y el consumidor corren al mismo tiempo (concurrencia con
asyncio) y se comunican por una cola:

- El **productor** trae comentarios de la fuente y los pone en la cola.
  Mientras tanto, el consumidor puede estar procesando la ventana anterior.
- La **cola** tiene tamaño máximo: si se llena, el productor espera
  (backpressure). Así la memoria no crece sin control.
- El **consumidor** agrupa lo que sale de la cola en ventanas de tiempo fijas
  (batching).
"""
import asyncio
import time
from collections.abc import AsyncIterator


async def produce(source: AsyncIterator[list[dict]], queue: asyncio.Queue) -> None:
    """Productor: pone en la cola cada comentario que entrega la fuente."""
    async for batch in source:
        for comment in batch:
            await queue.put(comment)  # si la cola está llena, espera acá


async def time_windows(queue: asyncio.Queue, seconds: float) -> AsyncIterator[list[dict]]:
    """Consumidor: agrupa lo que llega a la cola en ventanas de ``seconds`` segundos.

    Entrega una lista por ventana, aunque esté vacía, así el dashboard se
    actualiza igual cuando no hay comentarios nuevos.
    """
    while True:
        window = []
        end = time.monotonic() + seconds
        while (remaining := end - time.monotonic()) > 0:
            try:
                window.append(await asyncio.wait_for(queue.get(), timeout=remaining))
            except TimeoutError:
                break
        yield window
