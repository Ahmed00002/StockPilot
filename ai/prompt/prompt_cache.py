# ai/prompt/prompt_cache.py
import hashlib
import logging
from threading import Lock
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("PromptCache")

class PromptCache:
    """Thread-safe memory buffer managing identical request strings to bypass unnecessary provider dispatches."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, str]] = {}
        self._ttl_seconds = ttl_seconds
        self._lock = Lock()

    def _generate_key(self, workspace: str, image_hash: str, marketplace: str, language: str, provider: str, version: str) -> str:
        key_raw = f"{workspace}_{image_hash}_{marketplace}_{language}_{provider}_{version}"
        return hashlib.sha256(key_raw.encode("utf-8")).hexdigest()

    def get(self, workspace: str, image_hash: str, marketplace: str, language: str, provider: str, version: str) -> Optional[str]:
        key = self._generate_key(workspace, image_hash, marketplace, language, provider, version)
        
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
                
            timestamp = float(entry["timestamp"])
            if (datetime.now().timestamp() - timestamp) > self._ttl_seconds:
                del self._cache[key]
                return None
                
            logger.debug(f"Prompt cache hit identified for key boundary: {key[:8]}...")
            return entry["prompt"]

    def set(self, workspace: str, image_hash: str, marketplace: str, language: str, provider: str, version: str, prompt: str) -> None:
        key = self._generate_key(workspace, image_hash, marketplace, language, provider, version)
        
        with self._lock:
            self._cache[key] = {
                "prompt": prompt,
                "timestamp": str(datetime.now().timestamp())
            }
            
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            logger.info("Prompt runtime intelligence cache purged successfully.")