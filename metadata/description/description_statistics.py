# metadata/description/description_statistics.py
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

@dataclass
class DescStats:
    total_generated: int = 0
    average_length: float = 0.0
    average_seo_score: float = 0.0
    average_commercial_score: float = 0.0
    generation_times: List[float] = field(default_factory=list)
    validation_failures: Dict[str, int] = field(default_factory=dict)

class DescriptionStatistics:
    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> DescStats:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return DescStats(**data)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load desc statistics: {e}")
        return DescStats()

    def _save_stats(self) -> None:
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save desc statistics: {e}")

    def log_generation(self, length: int, seo_score: float, commercial_score: float, duration: float) -> None:
        t = self.stats.total_generated
        
        self.stats.average_length = ((self.stats.average_length * t) + length) / (t + 1)
        self.stats.average_seo_score = ((self.stats.average_seo_score * t) + seo_score) / (t + 1)
        self.stats.average_commercial_score = ((self.stats.average_commercial_score * t) + commercial_score) / (t + 1)
        
        self.stats.total_generated += 1
        self.stats.generation_times.append(duration)
        
        if len(self.stats.generation_times) > 1000:
            self.stats.generation_times = self.stats.generation_times[-1000:]
            
        self._save_stats()

    def log_validation_failure(self, reason: str) -> None:
        self.stats.validation_failures[reason] = self.stats.validation_failures.get(reason, 0) + 1
        self._save_stats()