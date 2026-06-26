# metadata/compliance/marketplace_registry.py
from typing import Dict, List
import logging

from metadata.compliance.base_marketplace import BaseMarketplace
from metadata.compliance.adobe_stock_rules import AdobeStockMarketplace

logger = logging.getLogger(__name__)

class MarketplaceRegistry:
    def __init__(self):
        self._marketplaces: Dict[str, BaseMarketplace] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register("adobe_stock", AdobeStockMarketplace())

    def register(self, key: str, marketplace: BaseMarketplace):
        self._marketplaces[key] = marketplace
        logger.info(f"Registered marketplace: {marketplace.name}")

    def get_marketplace(self, key: str) -> BaseMarketplace:
        if key not in self._marketplaces:
            logger.warning(f"Marketplace '{key}' not found, falling back to adobe_stock.")
            return self._marketplaces.get("adobe_stock", AdobeStockMarketplace())
        return self._marketplaces[key]
        
    def list_marketplaces(self) -> List[str]:
        return list(self._marketplaces.keys())