import time
from typing import Any, Dict, Tuple

class TTLCache:
    def __init__(self, ttl_seconds: int = 60, maxsize: int = 128):
        self.ttl = ttl_seconds
        self.maxsize = maxsize
        self._store: Dict[Any, Tuple[float, Any]] = {}

    def get(self, key: Any):
        now = time.time()
        v = self._store.get(key)
        if not v:
            return None
        ts, val = v
        if now - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return val

    def set(self, key: Any, val: Any):
        if len(self._store) >= self.maxsize:
            oldest = min(self._store.items(), key=lambda x: x[1][0])[0]
            self._store.pop(oldest, None)
        self._store[key] = (time.time(), val)
