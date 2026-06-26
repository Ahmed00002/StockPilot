# ai/prompt/prompt_statistics.py
import logging
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger("PromptStatistics")

@dataclass
class PromptStatsModel:
    total_prompts_built: int = 0
    average_prompt_length: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    validation_errors: int = 0
    total_optimization_savings_chars: int = 0

class PromptStatistics:
    """Thread-safe telemetry accumulator for tracking prompt generation operational health."""

    def __init__(self):
        self._stats = PromptStatsModel()
        self._lock = Lock()

    def record_build(self, length: int, optimization_savings: int) -> None:
        with self._lock:
            current_total = self._stats.total_prompts_built * self._stats.average_prompt_length
            self._stats.total_prompts_built += 1
            self._stats.average_prompt_length = (current_total + length) / self._stats.total_prompts_built
            self._stats.total_optimization_savings_chars += optimization_savings

    def record_cache_hit(self) -> None:
        with self._lock:
            self._stats.cache_hits += 1

    def record_cache_miss(self) -> None:
        with self._lock:
            self._stats.cache_misses += 1

    def record_validation_error(self) -> None:
        with self._lock:
            self._stats.validation_errors += 1

    def get_snapshot(self) -> PromptStatsModel:
        with self._lock:
            return PromptStatsModel(
                total_prompts_built=self._stats.total_prompts_built,
                average_prompt_length=self._stats.average_prompt_length,
                cache_hits=self._stats.cache_hits,
                cache_misses=self._stats.cache_misses,
                validation_errors=self._stats.validation_errors,
                total_optimization_savings_chars=self._stats.total_optimization_savings_chars
            )