# processing/batch_cache.py
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BatchCache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def remove(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()