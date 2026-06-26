# ai/provider_factory.py
import logging
from typing import Dict, Type, Callable, Optional

from ai.providers.base_provider import BaseProvider

logger = logging.getLogger("ProviderFactory")

class ProviderFactory:
    """
    Responsible for instantiating concrete implementations of AI providers.
    Uses a dynamic registration pattern to avoid hardcoding provider types.
    """

    def __init__(self) -> None:
        self._creators: Dict[str, Callable[[], BaseProvider]] = {}

    def register_creator(self, provider_type: str, creator_callable: Callable[[], BaseProvider]) -> None:
        """
        Registers a factory function or class constructor for a given provider type.
        
        Args:
            provider_type: The identifier for the type of provider.
            creator_callable: A callable returning a BaseProvider instance.
        """
        if provider_type in self._creators:
            logger.warning(f"Overwriting existing creator for provider type: {provider_type}")
        
        self._creators[provider_type] = creator_callable
        logger.debug(f"Registered creator for provider type: {provider_type}")

    def register_class(self, provider_type: str, provider_class: Type[BaseProvider]) -> None:
        """
        Registers a class type directly as the creator.
        
        Args:
            provider_type: The identifier for the type of provider.
            provider_class: The class inheriting from BaseProvider.
        """
        self.register_creator(provider_type, lambda: provider_class())

    def create(self, provider_type: str) -> BaseProvider:
        """
        Instantiates a provider of the requested type.
        
        Args:
            provider_type: The type identifier to instantiate.
            
        Returns:
            A new instance of a BaseProvider.
            
        Raises:
            ValueError: If the provider_type has not been registered.
        """
        creator = self._creators.get(provider_type)
        if not creator:
            logger.error(f"Provider type '{provider_type}' is not registered in the factory.")
            raise ValueError(f"Unknown provider type: {provider_type}")
            
        logger.debug(f"Creating new instance of provider type: {provider_type}")
        return creator()