# metadata/workspace/revision_statistics.py
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

@dataclass
class ImageRevisionStats:
    total_versions: int = 0
    merge_count: int = 0
    manual_edits: int = 0
    provider_usage: Dict[str, int] = field(default_factory=dict)
    average_score: float = 0.0
    best_score: float = 0.0
    best_version_id: str = ""

class RevisionStatistics:
    def __init__(self, workspace_dir: Path):
        self.stats_file = workspace_dir / "revision_stats.json"
        self._stats: Dict[str, ImageRevisionStats] = self._load_stats()

    def _load_stats(self) -> Dict[str, ImageRevisionStats]:
        if not self.stats_file.exists():
            return {}
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: ImageRevisionStats(**v) for k, v in data.items()}
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load revision stats: {e}")
            return {}

    def _save_stats(self) -> None:
        try:
            data = {k: asdict(v) for k, v in self._stats.items()}
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save revision stats: {e}")

    def get_stats(self, image_hash: str) -> ImageRevisionStats:
        if image_hash not in self._stats:
            self._stats[image_hash] = ImageRevisionStats()
        return self._stats[image_hash]

    def log_version(self, image_hash: str, version_id: str, provider: str, score: float, is_merge: bool, is_manual: bool):
        stats = self.get_stats(image_hash)
        
        stats.total_versions += 1
        stats.provider_usage[provider] = stats.provider_usage.get(provider, 0) + 1
        
        if is_merge:
            stats.merge_count += 1
        if is_manual:
            stats.manual_edits += 1
            
        if score > 0:
            total_score = (stats.average_score * (stats.total_versions - 1)) + score
            stats.average_score = total_score / stats.total_versions
            
            if score > stats.best_score:
                stats.best_score = score
                stats.best_version_id = version_id
                
        self._save_stats()