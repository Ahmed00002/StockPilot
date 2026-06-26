# processing/batch_statistics.py
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class ProcessingStats:
    total_processed: int = 0
    total_success: int = 0
    total_failed: int = 0
    average_duration: float = 0.0
    average_quality_score: float = 0.0
    average_compliance_score: float = 0.0
    provider_stats: Dict[str, int] = field(default_factory=dict)

class BatchStatistics:
    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> ProcessingStats:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ProcessingStats(**data)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load batch stats: {e}")
        return ProcessingStats()

    def _save_stats(self) -> None:
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save batch stats: {e}")

    def log_job_result(self, success: bool, duration: float, provider: str, quality: float = 0.0, compliance: float = 0.0) -> None:
        t = self.stats.total_processed
        
        self.stats.average_duration = ((self.stats.average_duration * t) + duration) / (t + 1)
        
        if success:
            s = self.stats.total_success
            self.stats.average_quality_score = ((self.stats.average_quality_score * s) + quality) / (s + 1)
            self.stats.average_compliance_score = ((self.stats.average_compliance_score * s) + compliance) / (s + 1)
            self.stats.total_success += 1
        else:
            self.stats.total_failed += 1
            
        self.stats.total_processed += 1
        self.stats.provider_stats[provider] = self.stats.provider_stats.get(provider, 0) + 1
        
        self._save_stats()