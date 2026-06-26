# metadata/keywords/keyword_marketplace.py
from dataclasses import dataclass
from typing import List

@dataclass
class MarketplaceRequirements:
    name: str
    max_keywords: int
    prioritize_ordering: bool
    allowed_special_chars: str = "-"

class AdobeStockMarketplace(MarketplaceRequirements):
    def __init__(self):
        super().__init__(
            name="adobe_stock",
            max_keywords=50,
            prioritize_ordering=True,
            allowed_special_chars="-"
        )

    def optimize_order(self, keywords: List[str], primary_subjects: List[str]) -> List[str]:
        ordered = []
        primary_set = set(primary_subjects)
        
        for kw in keywords:
            if kw in primary_set:
                ordered.append(kw)
                
        for kw in keywords:
            if kw not in primary_set:
                ordered.append(kw)
                
        return ordered[:self.max_keywords]

ADOBE_STOCK_RULES = AdobeStockMarketplace()