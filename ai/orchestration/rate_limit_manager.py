# ai/orchestration/rate_limit_manager.py
import time
import logging
from threading import Lock
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger("RateLimitManager")

@dataclass
class ProviderLimitConfig:
    requests_per_minute: int
    burst_limit: int

class GlobalRateLimitManager:
    """
    A unified rate limit tracking mechanism that sits above individual providers,
    allowing the Orchestrator to preemptively queue or delay requests before they
    reach the provider's localized SDK implementations.
    """

    def __init__(self):
        self._lock = Lock()
        self._limits: dict[str, ProviderLimitConfig] = {}
        self._request_history: dict[str, list[float]] = defaultdict(list)

    def set_provider_limit(self, provider_name: str, config: ProviderLimitConfig) -> None:
        with self._lock:
            self._limits[provider_name] = config

    def check_and_wait(self, provider_name: str) -> None:
        with self._lock:
            config = self._limits.get(provider_name)
            if not config:
                return  # No limit tracked at global level

            now = time.time()
            history = self._request_history[provider_name]
            
            # Prune older than 60 seconds
            history[:] = [ts for ts in history if now - ts < 60.0]

            if len(history) >= config.requests_per_minute:
                sleep_time = 60.0 - (now - history[0])
                if sleep_time > 0:
                    logger.info(f"Global orchestrator rate limit reached for {provider_name}. Delaying {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            
            self._request_history[provider_name].append(time.time())