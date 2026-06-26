# metadata/title/title_cache.py
import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    titles: List[str]
    provider: str
    prompt_version: str
    marketplace: str
    language: str

class TitleCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str) -> str:
        unique_string = f"{image_hash}_{prompt_version}_{marketplace}_{language}_{provider}"
        return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

    def get(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str) -> Optional[List[str]]:
        key = self._generate_key(image_hash, prompt_version, marketplace, language, provider)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Cache hit for {image_hash}")
                    return data.get("titles", [])
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Cache read error for {key}: {e}")
        
        logger.debug(f"Cache miss for {image_hash}")
        return None

    def set(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str, titles: List[str]) -> None:
        key = self._generate_key(image_hash, prompt_version, marketplace, language, provider)
        cache_file = self.cache_dir / f"{key}.json"
        
        entry = CacheEntry(
            titles=titles,
            provider=provider,
            prompt_version=prompt_version,
            marketplace=marketplace,
            language=language
        )
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(entry), f, indent=2)
            logger.info(f"Cached titles for {image_hash}")
        except IOError as e:
            logger.error(f"Failed to write cache for {key}: {e}")