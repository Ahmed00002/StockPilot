# ai/provider_manager.py
import logging
from threading import RLock
from typing import Callable, List, Optional

from ai.provider_factory import ProviderFactory
from ai.provider_registry import ProviderRegistry
from ai.providers.base_provider import BaseProvider

logger = logging.getLogger("ProviderManager")


class ProviderManager:
    """
    Coordinates provider creation, registration, enabled state, and shutdown.
    """

    def __init__(
        self,
        registry: Optional[ProviderRegistry] = None,
        factory: Optional[ProviderFactory] = None,
    ) -> None:
        self._registry = registry or ProviderRegistry()
        self._factory = factory or ProviderFactory()
        self._lock = RLock()

    def register_provider(self, name: str, provider: BaseProvider, enabled: bool = False) -> None:
        """Registers an instantiated provider and optionally enables it for routing."""
        with self._lock:
            self._registry.register(name, provider)
            if enabled:
                self._registry.enable(name)

    def register_provider_type(self, provider_type: str, creator: Callable[[], BaseProvider]) -> None:
        """Registers a provider factory callable for deferred creation."""
        with self._lock:
            self._factory.register_creator(provider_type, creator)

    def create_provider(self, name: str, provider_type: str, enabled: bool = False) -> BaseProvider:
        """Creates a provider from a registered factory type and stores it in the registry."""
        with self._lock:
            provider = self._factory.create(provider_type)
            self._registry.register(name, provider)
            if enabled:
                self._registry.enable(name)
            return provider

    def enable_provider(self, name: str) -> None:
        with self._lock:
            self._registry.enable(name)

    def disable_provider(self, name: str) -> None:
        with self._lock:
            self._registry.disable(name)

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Returns an enabled provider by name, or None when unavailable."""
        with self._lock:
            if not self._registry.is_enabled(name):
                return None
            return self._registry.find(name)

    def find_provider(self, name: str) -> Optional[BaseProvider]:
        """Returns a registered provider regardless of enabled state."""
        with self._lock:
            return self._registry.find(name)

    def get_all_active_providers(self) -> List[BaseProvider]:
        with self._lock:
            providers: List[BaseProvider] = []
            for name in self._registry.list_enabled():
                provider = self._registry.find(name)
                if provider is not None:
                    providers.append(provider)
            return providers

    def list_providers(self) -> List[str]:
        with self._lock:
            return self._registry.list_all()

    def list_active_providers(self) -> List[str]:
        with self._lock:
            return self._registry.list_enabled()

    def shutdown_all(self) -> None:
        """Best-effort shutdown for registered providers."""
        with self._lock:
            for name in self._registry.list_all():
                provider = self._registry.find(name)
                if provider is None:
                    continue
                try:
                    provider.shutdown()
                except Exception as exc:
                    logger.warning("Provider shutdown failed for %s: %s", name, exc)
