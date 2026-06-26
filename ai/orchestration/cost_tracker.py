# ai/orchestration/cost_tracker.py
import logging
from threading import Lock
from typing import Dict, Tuple
from dataclasses import dataclass
from ai.models import TokenUsage, CostEstimate

logger = logging.getLogger("CostTracker")

@dataclass
class PricingTier:
    input_cost_per_1k: float
    output_cost_per_1k: float

class CostTracker:
    """
    Translates raw token usage into monetary values using dynamic pricing tables,
    accumulating financial liabilities per workspace and provider.
    """

    def __init__(self):
        self._lock = Lock()
        self._pricing_tables: Dict[str, Dict[str, PricingTier]] = {}
        self._workspace_costs: Dict[str, float] = {}
        self._provider_costs: Dict[str, float] = {}
        self._global_cost = 0.0

    def update_pricing(self, provider: str, model: str, tier: PricingTier) -> None:
        """Allows external systems to update pricing without code changes."""
        with self._lock:
            if provider not in self._pricing_tables:
                self._pricing_tables[provider] = {}
            self._pricing_tables[provider][model] = tier
            logger.info(f"Updated pricing table for {provider}/{model}.")

    def calculate_and_record(self, workspace: str, provider: str, model: str, usage: TokenUsage) -> CostEstimate:
        """Calculates cost based on token split, records it, and returns the estimate."""
        cost_amount = 0.0
        
        with self._lock:
            provider_table = self._pricing_tables.get(provider, {})
            tier = provider_table.get(model)
            
            if tier:
                p_tokens = usage.prompt_tokens if isinstance(usage.prompt_tokens, int) else 0
                c_tokens = usage.response_tokens if isinstance(usage.response_tokens, int) else 0
                
                input_cost = (p_tokens / 1000.0) * tier.input_cost_per_1k
                output_cost = (c_tokens / 1000.0) * tier.output_cost_per_1k
                cost_amount = input_cost + output_cost

            # Record internal accumulation
            self._workspace_costs[workspace] = self._workspace_costs.get(workspace, 0.0) + cost_amount
            self._provider_costs[provider] = self._provider_costs.get(provider, 0.0) + cost_amount
            self._global_cost += cost_amount

        return CostEstimate(currency="USD", amount=cost_amount)

    def get_workspace_cost(self, workspace: str) -> float:
        with self._lock:
            return self._workspace_costs.get(workspace, 0.0)