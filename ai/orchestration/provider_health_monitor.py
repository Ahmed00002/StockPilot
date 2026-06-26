# ai/orchestration/provider_health_monitor.py
import logging
from threading import Lock
from typing import Dict
from datetime import datetime

logger = logging.getLogger("ProviderHealthMonitor")

class ProviderHealthMonitor:
    """
    Subsystem for maintaining real-time awareness of provider availability,
    allowing the Orchestrator to bypass offline infrastructure.
    """

    def __init__(self):
        self._lock = Lock()
        self._health_states: Dict[str, bool] = {}
        self._last_checked: Dict[str, datetime] = {}

    def update_health(self, provider_name: str, is_healthy: bool) -> None:
        with self._lock:
            old_state = self._health_states.get(provider_name, True)
            self._health_states[provider_name] = is_healthy
            self._last_checked[provider_name] = datetime.now()
            
            if old_state and not is_healthy:
                logger.warning(f"Health Monitor: Provider '{provider_name}' flagged as OFFLINE.")
            elif not old_state and is_healthy:
                logger.info(f"Health Monitor: Provider '{provider_name}' recovered and is ONLINE.")

    def is_healthy(self, provider_name: str) -> bool:
        with self._lock:
            # Assume healthy if unknown to prevent deadlocking new providers
            return self._health_states.get(provider_name, True)