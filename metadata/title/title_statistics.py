# metadata/title/title_statistics.py
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

@dataclass
class TitleStats:
    total_generated: int = 0
    average_length: float = 0.0
    average_score: float = 0.0
    generation_times: List[float] = field(default_factory=list)
    validation_failures: Dict[str, int] = field(default_factory=dict)
    
    @property
    def average_generation_time(self) -> float:
        if not self.generation_times:
            return 0.0
        return sum(self.generation_times) / len(self.generation_times)

class TitleStatistics:
    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> TitleStats:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return TitleStats(**data)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load statistics: {e}")
        return TitleStats()

    def _save_stats(self) -> None:
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save statistics: {e}")

    def log_generation(self, length: int, score: float, duration: float) -> None:
        total_len = self.stats.average_length * self.stats.total_generated
        total_score = self.stats.average_score * self.stats.total_generated
        
        self.stats.total_generated += 1
        self.stats.average_length = (total_len + length) / self.stats.total_generated
        self.stats.average_score = (total_score + score) / self.stats.total_generated
        self.stats.generation_times.append(duration)
        
        if len(self.stats.generation_times) > 1000:
            self.stats.generation_times = self.stats.generation_times[-1000:]
            
        self._save_stats()

    def log_validation_failure(self, reason: str) -> None:
        self.stats.validation_failures[reason] = self.stats.validation_failures.get(reason, 0) + 1
        self._save_stats()