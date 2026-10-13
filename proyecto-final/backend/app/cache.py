"""Cache LRU (Least Recently Used) con operaciones en O(1)."""
from collections import OrderedDict


class LRUCache:
    """Guarda hasta ``maxsize`` valores. Cuando se llena, descarta el menos usado.

    ``OrderedDict`` mantiene el orden de uso: ``move_to_end`` marca una clave
    como recién usada y ``popitem(last=False)`` saca la más vieja. Las dos
    operaciones son O(1).

    No se usa ``functools.lru_cache`` porque ese decorador memoiza llamadas a
    una función de a un argumento por vez, y acá los textos se procesan por lote.
    """

    def __init__(self, maxsize: int = 10_000):
        self.maxsize = maxsize
        self._data: OrderedDict = OrderedDict()

    def get(self, key):
        """Devuelve el valor guardado, o None si no está."""
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key, value) -> None:
        """Guarda un valor; si se supera ``maxsize``, descarta el menos usado."""
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self.maxsize:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)
