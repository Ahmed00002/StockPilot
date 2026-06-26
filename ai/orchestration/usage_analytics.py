# ai/orchestration/usage_analytics.py
import logging
from threading import Lock
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger("UsageAnalytics")

@dataclass
class AnalyticsSnapshot:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_execution_time_ms: float = 0.0
    total_cost: float = 0.0
    total_tokens: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100.0

    @property
    def average_response_time_ms(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_execution_time_ms / self.successful_requests

    @property
    def average_cost_per_request(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_cost / self.successful_requests

class UsageAnalytics:
    """
    Maintains rolled-up mathematical aggregates of system performance for dashboarding.
    """

    def __init__(self):
        self._lock = Lock()
        self._global_stats = AnalyticsSnapshot()
        self._provider_stats: Dict[str, AnalyticsSnapshot] = {}

    def record_success(self, provider_name: str, execution_time_ms: float, cost: float, tokens: int) -> None:
        with self._lock:
            self._global_stats.total_requests += 1
            self._global_stats.successful_requests += 1
            self._global_stats.total_execution_time_ms += execution_time_ms
            self._global_stats.total_cost += cost
            self._global_stats.total_tokens += tokens

            if provider_name not in self._provider_stats:
                self._provider_stats[provider_name] = AnalyticsSnapshot()
                
            p_stats = self._provider_stats[provider_name]
            p_stats.total_requests += 1
            p_stats.successful_requests += 1
            p_stats.total_execution_time_ms += execution_time_ms
            p_stats.total_cost += cost
            p_stats.total_tokens += tokens

    def record_failure(self, provider_name: str = "unknown") -> None:
        with self._lock:
            self._global_stats.total_requests += 1
            self._global_stats.failed_requests += 1

            if provider_name != "unknown":
                if provider_name not in self._provider_stats:
                    self._provider_stats[provider_name] = AnalyticsSnapshot()
                self._provider_stats[provider_name].total_requests += 1
                self._provider_stats[provider_name].failed_requests += 1

    def get_global_analytics(self) -> AnalyticsSnapshot:
        with self._lock:
            return AnalyticsSnapshot(**self._global_stats.__dict__)