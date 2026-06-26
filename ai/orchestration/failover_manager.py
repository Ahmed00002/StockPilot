# ai/orchestration/failover_manager.py
import logging
from threading import Lock
from typing import Dict

logger = logging.getLogger("FailoverManager")


class FailoverManager:
    """
    Decides whether a provider failure should trigger routing to another provider.
    """

    def __init__(self, max_failovers_per_provider: int = 3) -> None:
        self._max_failovers_per_provider = max_failovers_per_provider
        self._failover_counts: Dict[str, int] = {}
        self._lock = Lock()

    def should_failover(self, error: Exception, provider_name: str) -> bool:
        """Returns True for transient provider failures while limiting repeated churn."""
        error_name = type(error).__name__.lower()
        error_message = str(error).lower()

        if any(marker in error_name or marker in error_message for marker in ("auth", "credential", "permission")):
            return False
        if any(marker in error_message for marker in ("invalid request", "malformed", "unsupported")):
            return False

        transient = any(
            marker in error_name or marker in error_message
            for marker in ("timeout", "rate", "429", "network", "connection", "unavailable", "5")
        )
        if not transient:
            return False

        with self._lock:
            count = self._failover_counts.get(provider_name, 0)
            if count >= self._max_failovers_per_provider:
                logger.warning("Failover limit reached for provider '%s'.", provider_name)
                return False
            self._failover_counts[provider_name] = count + 1
            return True

    def reset_provider(self, provider_name: str) -> None:
        with self._lock:
            self._failover_counts.pop(provider_name, None)
