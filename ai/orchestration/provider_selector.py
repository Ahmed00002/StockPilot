# ai/orchestration/provider_selector.py
import logging
from typing import List, Set, Optional

from ai.models import AIRequest
from ai.request_context import RequestContext
from ai.provider_manager import ProviderManager

from .routing_engine import RoutingEngine, RoutingStrategy
from .provider_priority import ProviderPriority

logger = logging.getLogger("ProviderSelector")

class ProviderSelector:
    """
    Coordinates available providers from AIManager with the Orchestrator's Routing Engine.
    """

    def __init__(
        self, 
        provider_manager: ProviderManager, 
        routing_engine: RoutingEngine,
        provider_priority: ProviderPriority
    ):
        self._provider_manager = provider_manager
        self._routing_engine = routing_engine
        self._provider_priority = provider_priority

    def select_provider(
        self, 
        request: AIRequest, 
        context: RequestContext, 
        excluded_providers: Set[str]
    ) -> Optional[str]:
        
        # Determine strategy from context user settings, default to balanced
        strategy_str = context.get_setting("routing_strategy", "balanced")
        try:
            strategy = RoutingStrategy(strategy_str.lower())
        except ValueError:
            strategy = RoutingStrategy.BALANCED
            
        active_providers = self._provider_manager.get_all_active_providers()
        available_names = [
            p.get_provider_information().name 
            for p in active_providers 
            if p.get_provider_information().name not in excluded_providers
        ]
        
        if not available_names:
            logger.error("Provider selection failed: No available providers match the criteria.")
            return None
            
        # Apply strict priority ordering to the candidates
        ordered_candidates = self._provider_priority.sort_providers(available_names)

        # If strategy is manual, strict adherence to priority list is required
        if strategy == RoutingStrategy.MANUAL:
            selected = ordered_candidates[0]
            logger.debug(f"Manual routing selected provider: {selected}")
            return selected
            
        # Otherwise, delegate to the intelligence routing engine
        selected = self._routing_engine.evaluate(ordered_candidates, strategy, request, context)
        logger.debug(f"Routing engine ({strategy.value}) selected provider: {selected}")
        
        return selected