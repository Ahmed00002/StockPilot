# ai/provider_registry.py
import logging
from typing import Dict, List, Optional

from ai.providers.base_provider import BaseProvider

logger = logging.getLogger("ProviderRegistry")

class ProviderRegistry:
    """
    Maintains the state and lifecycle status of all instantiated AI Providers.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}
        self._enabled_status: Dict[str, bool] = {}

    def register(self, name: str, provider: BaseProvider) -> None:
        """
        Registers a new provider instance into the system.
        
        Args:
            name: The unique system name for the provider.
            provider: The instantiated provider object.
        """
        if name in self._providers:
            logger.warning(f"Provider '{name}' is already registered. Overwriting.")
        
        self._providers[name] = provider
        self._enabled_status[name] = False
        logger.info(f"Registered provider: {name}")

    def unregister(self, name: str) -> None:
        """
        Removes a provider from the registry.
        
        Args:
            name: The unique system name of the provider.
        """
        if name in self._providers:
            del self._providers[name]
            del self._enabled_status[name]
            logger.info(f"Unregistered provider: {name}")
        else:
            logger.warning(f"Attempted to unregister unknown provider: {name}")

    def find(self, name: str) -> Optional[BaseProvider]:
        """
        Retrieves a provider by its registered name.
        
        Args:
            name: The unique system name.
            
        Returns:
            The provider instance, or None if not found.
        """
        return self._providers.get(name)

    def enable(self, name: str) -> None:
        """
        Marks a registered provider as enabled and ready for selection.
        
        Args:
            name: The name of the provider to enable.
        """
        if name in self._enabled_status:
            self._enabled_status[name] = True
            logger.info(f"Enabled provider: {name}")
        else:
            logger.error(f"Cannot enable unknown provider: {name}")

    def disable(self, name: str) -> None:
        """
        Marks a registered provider as disabled.
        
        Args:
            name: The name of the provider to disable.
        """
        if name in self._enabled_status:
            self._enabled_status[name] = False
            logger.info(f"Disabled provider: {name}")
        else:
            logger.error(f"Cannot disable unknown provider: {name}")

    def is_enabled(self, name: str) -> bool:
        """
        Checks if a specific provider is currently enabled.
        
        Args:
            name: The provider name.
            
        Returns:
            True if registered and enabled, False otherwise.
        """
        return self._enabled_status.get(name, False)

    def list_all(self) -> List[str]:
        """
        Lists the names of all registered providers.
        
        Returns:
            List of registered provider names.
        """
        return list(self._providers.keys())

    def list_enabled(self) -> List[str]:
        """
        Lists the names of all providers currently marked as enabled.
        
        Returns:
            List of enabled provider names.
        """
        return [name for name, enabled in self._enabled_status.items() if enabled]