# ai/orchestration/provider_benchmark.py
import logging
from threading import Lock
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("ProviderBenchmark")

@dataclass
class BenchmarkEntry:
    latency_ms: float
    success: bool
    cost_per_1k: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

class ProviderBenchmark:
    """
    Continuously measures and stores historical execution speeds and reliability metrics
    for the Routing Engine to make dynamic algorithmic choices.
    """

    def __init__(self, window_size: int = 100):
        self._lock = Lock()
        self._window_size = window_size
        self._history: Dict[str, List[BenchmarkEntry]] = {}
        self._capabilities: Dict[str, Dict[str, float]] = {}

    def record_execution(self, provider_name: str, latency: float, success: bool, cost_per_1k: float = 0.0) -> None:
        with self._lock:
            if provider_name not in self._history:
                self._history[provider_name] = []
                
            history = self._history[provider_name]
            history.insert(0, BenchmarkEntry(latency_ms=latency, success=success, cost_per_1k=cost_per_1k))
            
            if len(history) > self._window_size:
                history.pop()

    def register_capability(self, provider_name: str, capability: str, score: float) -> None:
        with self._lock:
            if provider_name not in self._capabilities:
                self._capabilities[provider_name] = {}
            self._capabilities[provider_name][capability] = score

    def get_average_latency(self, provider_name: str) -> float:
        with self._lock:
            history = self._history.get(provider_name, [])
            successful = [e.latency_ms for e in history if e.success]
            if not successful:
                return float('inf')
            return sum(successful) / len(successful)

    def get_success_rate(self, provider_name: str) -> float:
        with self._lock:
            history = self._history.get(provider_name, [])
            if not history:
                return 1.0 # Optimistic initial assumption
            successful = sum(1 for e in history if e.success)
            return successful / len(history)

    def get_average_cost_per_1k_tokens(self, provider_name: str) -> float:
        with self._lock:
            history = self._history.get(provider_name, [])
            if not history:
                return 0.0
            return sum(e.cost_per_1k for e in history) / len(history)

    def supports_capability(self, provider_name: str, capability: str) -> bool:
        with self._lock:
            caps = self._capabilities.get(provider_name, {})
            return capability in caps

    def get_capability_score(self, provider_name: str, capability: str) -> float:
        with self._lock:
            caps = self._capabilities.get(provider_name, {})
            return caps.get(capability, 0.0)