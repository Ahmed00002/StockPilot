# core/dependency_container.py
from core.event_bus import EventBus
from core.config_manager import ConfigManager
from core.theme_manager import ThemeManager
from workspace.workspace_manager import WorkspaceManager
from image.image_manager import ImageManager

class DependencyContainer:
    """IoC Container for managing application services and singletons."""
    
    def __init__(self) -> None:
        self.services = {}
        
        # Initialize Core Services
        self.event_bus = EventBus()
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager(self.event_bus)
        self.workspace_manager = WorkspaceManager(self.event_bus)
        self.image_manager = ImageManager(self.event_bus)

        # Register Services for UI Consumption
        self.register_service("event_bus", self.event_bus)
        self.register_service("config_manager", self.config_manager)
        self.register_service("theme_manager", self.theme_manager)
        self.register_service("workspace_manager", self.workspace_manager)
        self.register_service("image_manager", self.image_manager)

    def register_service(self, name: str, service: object) -> None:
        """Registers a new service instance."""
        self.services[name] = service

    def get_service(self, name: str) -> object:
        """Retrieves a registered service instance."""
        return self.services.get(name)