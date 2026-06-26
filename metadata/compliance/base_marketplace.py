# metadata/compliance/base_marketplace.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class MarketplaceRules:
    min_title_length: int = 5
    max_title_length: int = 200
    max_desc_length: int = 500
    min_keywords: int = 5
    max_keywords: int = 50

class BaseMarketplace(ABC):
    def __init__(self, name: str):
        self.name = name
        self.rules = MarketplaceRules()

    @abstractmethod
    def get_rules(self) -> MarketplaceRules:
        pass

    @abstractmethod
    def format_export(self, title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
        pass