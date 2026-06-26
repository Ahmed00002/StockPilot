# metadata/review/review_statistics.py
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

@dataclass
class ReviewStats:
    total_reviews: int = 0
    total_improvements: int = 0
    average_initial_score: float = 0.0
    average_final_score: float = 0.0
    common_warnings: Dict[str, int] = field(default_factory=dict)
    common_criticals: Dict[str, int] = field(default_factory=dict)

class ReviewStatistics:
    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> ReviewStats:
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ReviewStats(**data)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load review stats: {e}")
        return ReviewStats()

    def _save_stats(self) -> None:
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save review stats: {e}")

    def log_review(self, report: Any, is_final: bool) -> None:
        t = self.stats.total_reviews
        
        if report.revision_count == 0:
            self.stats.average_initial_score = ((self.stats.average_initial_score * t) + report.overall_score) / (t + 1)
            self.stats.total_reviews += 1
            
        if is_final:
            f = t if report.revision_count == 0 else self.stats.total_reviews
            self.stats.average_final_score = ((self.stats.average_final_score * max(1, f-1)) + report.overall_score) / max(1, f)
            if report.revision_count > 0:
                self.stats.total_improvements += 1

        for w in report.warnings:
            cat = w.category
            self.stats.common_warnings[cat] = self.stats.common_warnings.get(cat, 0) + 1
            
        for c in report.critical_errors:
            cat = c.category
            self.stats.common_criticals[cat] = self.stats.common_criticals.get(cat, 0) + 1
            
        self._save_stats()
