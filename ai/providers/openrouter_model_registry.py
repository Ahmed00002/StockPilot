# ai/providers/openrouter_model_registry.py
import logging
from threading import Lock
from typing import List, Dict, Optional
from datetime import datetime

from .openrouter_models import OpenRouterModelMeta

logger = logging.getLogger("OpenRouterModelRegistry")

class OpenRouterModelRegistry:
    """Thread-safe dynamic catalog tracking, searching, filtering, and caching metrics for OpenRouter models."""

    def __init__(self):
        self._models: Dict[str, OpenRouterModelMeta] = {}
        self._lock = Lock()
        self.last_cache_refresh: Optional[datetime] = None

    def update_registry(self, discovered_models: List[OpenRouterModelMeta]) -> None:
        """Overwrites local directory metadata states securely using external endpoint listings."""
        with self._lock:
            self._models.clear()
            for model in discovered_models:
                self._models[model.id] = model
            self.last_cache_refresh = datetime.now()
        logger.info(f"OpenRouter Model Registry flushed and populated with {len(discovered_models)} models.")

    def get_model(self, model_id: str) -> Optional[OpenRouterModelMeta]:
        with self._lock:
            return self._models.get(model_id)

    def get_all_models(self) -> List[OpenRouterModelMeta]:
        with self._lock:
            return list(self._models.values())

    def filter_and_sort_registry(
        self, 
        search_query: str = "", 
        provider_filter: str = "", 
        required_capability: Optional[str] = None,
        sort_by: str = "id"  # choices: id, pricing, context_length
    ) -> List[OpenRouterModelMeta]:
        """Provides high-velocity multi-axis slicing and arrangement options against active registries."""
        with self._lock:
            working_set = list(self._models.values())

        # Filter operations
        if search_query:
            query = search_query.lower()
            working_set = [m for m in working_set if query in m.id.lower() or query in m.name.lower()]

        if provider_filter:
            p_filter = provider_filter.lower()
            working_set = [m for m in working_set if p_filter in m.provider.lower()]

        if required_capability:
            from .openrouter_capabilities import OpenRouterCapabilities
            working_set = [m for m in working_set if OpenRouterCapabilities.verify_capability(m, required_capability)]

        # Sort operations
        if sort_by == "pricing":
            working_set.sort(key=lambda m: (m.input_cost_per_token + m.output_cost_per_token))
        elif sort_by == "context_length":
            working_set.sort(key=lambda m: m.context_length, reverse=True)
        else:
            working_set.sort(key=lambda m: m.id)

        return working_set