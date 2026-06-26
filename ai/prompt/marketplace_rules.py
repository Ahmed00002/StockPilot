# ai/prompt/marketplace_rules.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class MarketplaceRuleDefinition:
    title_max_length: int
    description_max_length: int
    keyword_max_count: int
    keyword_min_count: int
    restricted_terms: List[str]
    formatting_instructions: str

class MarketplaceRulesEngine:
    """Provides specific structural guidelines requested by distinct marketplace distribution channels."""

    _RULES: Dict[str, MarketplaceRuleDefinition] = {
        "Adobe Stock": MarketplaceRuleDefinition(
            title_max_length=200,
            description_max_length=200,
            keyword_max_count=50,
            keyword_min_count=5,
            restricted_terms=["editorial", "brand", "logo", "watermark", "generative ai"],
            formatting_instructions="Keywords must be comma-separated, ordered by relevance. Titles should be concise."
        ),
        "Shutterstock": MarketplaceRuleDefinition(
            title_max_length=200,
            description_max_length=200, # Shutterstock merges title/desc conceptually often, capping at 200.
            keyword_max_count=50,
            keyword_min_count=7,
            restricted_terms=["instagram", "pinterest", "tiktok", "generative ai"],
            formatting_instructions="Keywords must be strictly lowercase, comma-separated. Do not use special characters in titles."
        ),
        "Freepik": MarketplaceRuleDefinition(
            title_max_length=150,
            description_max_length=250,
            keyword_max_count=50,
            keyword_min_count=10,
            restricted_terms=["ai generated", "midjourney", "dalle", "stable diffusion"],
            formatting_instructions="Keywords should include both specific elements and broad conceptual terms."
        )
    }

    @staticmethod
    def get_rules(marketplace_name: str) -> Optional[MarketplaceRuleDefinition]:
        return MarketplaceRulesEngine._RULES.get(marketplace_name)

    @staticmethod
    def get_all_supported() -> List[str]:
        return list(MarketplaceRulesEngine._RULES.keys())