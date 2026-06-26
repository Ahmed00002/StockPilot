# core/dependency_container.py
import os
from pathlib import Path

from core.event_bus import EventBus
from core.config_manager import ConfigManager
from core.theme_manager import ThemeManager
from workspace.workspace_manager import WorkspaceManager
from image.image_manager import ImageManager

# Add missing imports for integration
from ai.provider_manager import ProviderManager
from ai.manager import AIManager
from metadata.workspace.workspace_manager import MetadataWorkspaceManager
from metadata.review.review_engine import MetadataReviewEngine
from integration.integration_manager import PipelineIntegrationManager

from metadata.compliance.compliance_engine import MarketplaceComplianceEngine
from metadata.title.title_engine import TitleIntelligenceEngine
from metadata.description.description_engine import DescriptionIntelligenceEngine


class _DummyVisionEngine:
    def process(self, image_path: str): return {}
    def is_healthy(self): return True

class _DummyKwEngine:
    class _Generator:
        def generate_candidate_pool(self, ctx): return []
    def __init__(self):
        self.generator = self._Generator()
    def process_pipeline(self, image_hash, pool, marketplace, language): return {}
    def is_healthy(self): return True


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
        
        # Initialize AI Services
        self.provider_manager = ProviderManager()
        self.ai_manager = AIManager(self.provider_manager)
        
        # Base Dir for Metadata Engines
        base_dir = Path(os.getcwd()) / "data"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Integration Managers
        self.metadata_workspace_manager = MetadataWorkspaceManager(base_dir)
        self.metadata_review_engine = MetadataReviewEngine(self.ai_manager)
        self.compliance_engine = MarketplaceComplianceEngine()
        self.title_engine = TitleIntelligenceEngine(self.ai_manager, base_dir)
        self.desc_engine = DescriptionIntelligenceEngine(self.ai_manager, base_dir)
        
        self.integration_manager = PipelineIntegrationManager(
            ai_manager=self.ai_manager,
            vision_engine=_DummyVisionEngine(),
            title_engine=self.title_engine,
            desc_engine=self.desc_engine,
            kw_engine=_DummyKwEngine(),
            review_engine=self.metadata_review_engine,
            compliance_engine=self.compliance_engine,
            workspace_manager=self.metadata_workspace_manager
        )

        # Register Services for UI Consumption
        self.register_service("event_bus", self.event_bus)
        self.register_service("config_manager", self.config_manager)
        self.register_service("theme_manager", self.theme_manager)
        self.register_service("workspace_manager", self.workspace_manager)
        self.register_service("image_manager", self.image_manager)
        self.register_service("provider_manager", self.provider_manager)
        self.register_service("ai_manager", self.ai_manager)
        self.register_service("metadata_workspace_manager", self.metadata_workspace_manager)
        self.register_service("metadata_review_engine", self.metadata_review_engine)
        self.register_service("integration_manager", self.integration_manager)

    def register_service(self, name: str, service: object) -> None:
        """Registers a new service instance."""
        self.services[name] = service

    def get_service(self, name: str) -> object:
        """Retrieves a registered service instance."""
        return self.services.get(name)