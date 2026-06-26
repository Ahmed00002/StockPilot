# ai/orchestration/routing_engine.py
import logging
from enum import Enum
from typing import List, Optional, Dict, Any

from ai.models import AIRequest
from ai.request_context import RequestContext
from .provider_benchmark import ProviderBenchmark
from .provider_health_monitor import ProviderHealthMonitor

logger = logging.getLogger("RoutingEngine")

class RoutingStrategy(Enum):
    MANUAL = "manual"
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    BEST_VISION = "best_vision"
    BEST_REASONING = "best_reasoning"
    MOST_RELIABLE = "most_reliable"
    BALANCED = "balanced"

class RoutingEngine:
    """
    Evaluates dynamic rules, benchmarks, and health metrics to determine the optimal provider.
    """

    def __init__(self, benchmark: ProviderBenchmark, health_monitor: ProviderHealthMonitor):
        self._benchmark = benchmark
        self._health_monitor = health_monitor

    def evaluate(
        self, 
        active_providers: List[str], 
        strategy: RoutingStrategy, 
        request: AIRequest,
        context: RequestContext
    ) -> Optional[str]:
        
        if not active_providers:
            return None

        healthy_providers = [p for p in active_providers if self._health_monitor.is_healthy(p)]
        
        if not healthy_providers:
            logger.warning("No healthy providers available. Falling back to all active providers.")
            candidates = active_providers
        else:
            candidates = healthy_providers

        if len(candidates) == 1:
            return candidates[0]

        if strategy == RoutingStrategy.FASTEST:
            return min(candidates, key=lambda p: self._benchmark.get_average_latency(p))
            
        elif strategy == RoutingStrategy.CHEAPEST:
            return min(candidates, key=lambda p: self._benchmark.get_average_cost_per_1k_tokens(p))
            
        elif strategy == RoutingStrategy.MOST_RELIABLE:
            return max(candidates, key=lambda p: self._benchmark.get_success_rate(p))
            
        elif strategy == RoutingStrategy.BEST_VISION:
            vision_capable = [p for p in candidates if self._benchmark.supports_capability(p, "vision")]
            if vision_capable:
                return max(vision_capable, key=lambda p: self._benchmark.get_capability_score(p, "vision"))
                
        elif strategy == RoutingStrategy.BEST_REASONING:
            reasoning_capable = [p for p in candidates if self._benchmark.supports_capability(p, "reasoning")]
            if reasoning_capable:
                return max(reasoning_capable, key=lambda p: self._benchmark.get_capability_score(p, "reasoning"))
                
        elif strategy == RoutingStrategy.BALANCED:
            # Simple scoring: Normalize reliability and latency
            def balanced_score(p: str) -> float:
                reliability = self._benchmark.get_success_rate(p) # 0.0 to 1.0
                latency = self._benchmark.get_average_latency(p) # in ms
                latency_penalty = min(latency / 5000.0, 1.0) # max penalty at 5s
                return reliability - (latency_penalty * 0.3)
            
            return max(candidates, key=balanced_score)

        # Default or Manual fallback (assumes the list is ordered by priority)
        return candidates[0]