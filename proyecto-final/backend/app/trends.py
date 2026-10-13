"""Tendencias: hashtags más usados en los últimos ``seconds`` segundos.

Funciona como un cache de conteos con vencimiento por tiempo (TTL): cada
ventana suma sus hashtags y, pasado ``seconds``, se descuenta sola. Así las
tendencias muestran lo que se repite durante el último minuto (no solo en la
ventana actual) y lo viejo se invalida automáticamente.
"""
from collections import Counter, deque


class TrendingHashtags:
    """Conteo de hashtags en una ventana deslizante de ``seconds`` segundos.

    Como el tiempo siempre avanza, la ventana que vence primero es la que
    entró primero: alcanza con una deque (FIFO), no hace falta un heap.
    """

    def __init__(self, seconds: float = 60):
        self.seconds = seconds
        self.totals: Counter = Counter()
        self._windows: deque = deque()  # (momento, conteo de esa ventana)

    def add(self, counts: Counter, now: float) -> None:
        """Suma el conteo de una ventana y descuenta las ventanas vencidas."""
        self.totals.update(counts)
        self._windows.append((now, counts))
        # La ventana recién agregada nunca vence, así que la deque nunca queda vacía.
        while now - self._windows[0][0] > self.seconds:
            _, old = self._windows.popleft()
            self.totals.subtract(old)
            for tag in old:
                if self.totals[tag] <= 0:
                    del self.totals[tag]

    def top(self, k: int = 10) -> list[tuple[str, int]]:
        """Los ``k`` hashtags más usados en los últimos ``seconds`` segundos."""
        return self.totals.most_common(k)
