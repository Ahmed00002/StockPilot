# metadata/compliance/adobe_stock_rules.py
from typing import List, Dict, Any
from metadata.compliance.base_marketplace import BaseMarketplace, MarketplaceRules

class AdobeStockMarketplace(BaseMarketplace):
    def __init__(self):
        super().__init__("Adobe Stock")
        self.rules = MarketplaceRules(
            min_title_length=5,
            max_title_length=200,
            max_desc_length=500,
            min_keywords=5,
            max_keywords=50
        )

    def get_rules(self) -> MarketplaceRules:
        return self.rules

    def format_export(self, title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        return {
            "title": title[:self.rules.max_title_length],
            "keywords": keywords[:self.rules.max_keywords],
            "category": 0 
        }