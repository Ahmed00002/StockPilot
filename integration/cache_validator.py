# integration/cache_validator.py
import logging
from typing import Any
import hashlib

logger = logging.getLogger(__name__)

class CacheValidator:
    def __init__(self, title_engine: Any, desc_engine: Any, kw_engine: Any):
        self.title_engine = title_engine
        self.desc_engine = desc_engine
        self.kw_engine = kw_engine

    def validate_cache_integrity(self, image_hash: str, marketplace: str, language: str, provider: str, prompt_version: str) -> bool:
        try:
            t_cache = self.title_engine.cache.get(image_hash, prompt_version, marketplace, language, provider)
            d_cache = self.desc_engine.cache.get(image_hash, prompt_version, marketplace, language, provider)
            k_cache = self.kw_engine.cache.get(image_hash, prompt_version, marketplace, language, provider)
            
            is_valid = bool(t_cache) and bool(d_cache) and bool(k_cache)
            if is_valid:
                logger.debug(f"Cache integrity verified for {image_hash}")
            else:
                logger.debug(f"Cache miss or incomplete for {image_hash}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating cache integrity: {e}")
            return False