# core/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path

class IStorage(ABC):
    """Base interface for all storage mechanisms."""
    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> bool:
        """Saves data to storage."""
        raise NotImplementedError
        
    @abstractmethod
    def load(self, key: str) -> Dict[str, Any]:
        """Loads data from storage."""
        raise NotImplementedError

class IAiProvider(ABC):
    """Base interface for AI metadata generation providers."""
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initializes the provider with credentials."""
        raise NotImplementedError
        
    @abstractmethod
    def generate_metadata(self, image_path: Path, prompt: str) -> Dict[str, Any]:
        """Generates metadata for a given image."""
        raise NotImplementedError

class IExporter(ABC):
    """Base interface for marketplace exporters."""
    @abstractmethod
    def export(self, data: List[Dict[str, Any]], destination: Path) -> bool:
        """Exports formatted data to a file."""
        raise NotImplementedError

class IPlugin(ABC):
    """Base interface for third-party plugins."""
    @abstractmethod
    def on_load(self) -> bool:
        """Called when the plugin is loaded into the system."""
        raise NotImplementedError
        
    @abstractmethod
    def on_unload(self) -> None:
        """Called when the plugin is being removed or application is shutting down."""
        raise NotImplementedError

class IWorkspaceManager(ABC):
    """Base interface for workspace management."""
    @abstractmethod
    def create_workspace(self, name: str) -> bool:
        """Creates a new workspace."""
        raise NotImplementedError
        
    @abstractmethod
    def load_workspace(self, name: str) -> bool:
        """Loads an existing workspace."""
        raise NotImplementedError