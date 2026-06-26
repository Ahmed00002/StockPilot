# metadata/description/description_cache.py
import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

@dataclass
class DescCacheEntry:
    descriptions: List[str]
    provider: str
    prompt_version: str
    marketplace: str
    language: str

class DescriptionCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str) -> str:
        unique_string = f"desc_{image_hash}_{prompt_version}_{marketplace}_{language}_{provider}"
        return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

    def get(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str) -> Optional[List[str]]:
        key = self._generate_key(image_hash, prompt_version, marketplace, language, provider)
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Description cache hit for {image_hash}")
                    return data.get("descriptions", [])
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Description cache read error: {e}")
        
        return None

    def set(self, image_hash: str, prompt_version: str, marketplace: str, language: str, provider: str, descriptions: List[str]) -> None:
        key = self._generate_key(image_hash, prompt_version, marketplace, language, provider)
        cache_file = self.cache_dir / f"{key}.json"
        
        entry = DescCacheEntry(
            descriptions=descriptions,
            provider=provider,
            prompt_version=prompt_version,
            marketplace=marketplace,
            language=language
        )
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(entry), f, indent=2)
        except IOError as e:
            logger.error(f"Failed to write description cache: {e}")