# ai/prompt/provider_rules.py
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("ProviderRules")

@dataclass
class ProviderAdjustment:
    instruction_additions: List[str]
    instruction_removals: List[str]
    optimal_temperature: Optional[float]
    optimal_top_p: Optional[float]

class ProviderRulesEngine:
    """Adapts raw prompt intent parameters into provider-specific optimal syntactic shapes."""

    _ADJUSTMENTS: Dict[str, ProviderAdjustment] = {
        "Gemini": ProviderAdjustment(
            instruction_additions=["Avoid using markdown bolding in keyword lists.", "Format output precisely as requested without conversational filler."],
            instruction_removals=[],
            optimal_temperature=0.7,
            optimal_top_p=0.9
        ),
        "OpenAI": ProviderAdjustment(
            instruction_additions=["Return strictly the requested structure. Do not include 'Here is the metadata:'."],
            instruction_removals=[],
            optimal_temperature=0.6, # Slightly lower for consistent metadata arrays
            optimal_top_p=1.0
        ),
        "Claude": ProviderAdjustment(
            instruction_additions=["Skip preamble. Produce only the finalized data structure."],
            instruction_removals=[],
            optimal_temperature=0.5,
            optimal_top_p=None
        ),
        "DeepSeek": ProviderAdjustment(
            instruction_additions=["Follow all structural rules explicitly. Output plain text formats only where requested."],
            instruction_removals=[],
            optimal_temperature=1.0,
            optimal_top_p=None
        )
    }

    @staticmethod
    def get_adjustment(provider_family: str) -> Optional[ProviderAdjustment]:
        for key, adj in ProviderRulesEngine._ADJUSTMENTS.items():
            if key.lower() in provider_family.lower():
                return adj
        logger.debug(f"No specific rule adjustments mapped for provider family: {provider_family}")
        return None