import time
from typing import Any, Dict, Tuple


class TTLCache:
    def __init__(self):
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Any:
        rec = self._store.get(key)
        if not rec:
            return None
        expires_at, value = rec
        if time.time() > expires_at:
            try:
                del self._store[key]
            except Exception:
                pass
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)


cache = TTLCache()
