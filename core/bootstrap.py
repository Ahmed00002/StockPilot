# core/bootstrap.py
from core.logger import setup_logging
from core.environment import EnvironmentChecker
from core.directories import DirectoryInitializer
from core.dependency_container import DependencyContainer
from core.lifecycle import ApplicationLifecycleManager
from core.constants import AppConstants

# Metadata/AI Services
from metadata.review.review_engine import MetadataReviewEngine

# Integration Services
from processing.batch_manager import BatchManager
from integration.integration_manager import PipelineIntegrationManager

class ApplicationBootstrap:
    """Master orchestrator for preparing the application environment."""

    @staticmethod
    def run() -> DependencyContainer:
        """Prepares environment, initializes core services, and returns the IoC container."""
        EnvironmentChecker.check_python_version()
        DirectoryInitializer.initialize()
        setup_logging()
        
        container = DependencyContainer()
        lifecycle = ApplicationLifecycleManager(container)
        
        lifecycle.start()
        container.register_service("lifecycle", lifecycle)
        
        # Initialize Core Engines
        ai_manager = container.get_service("ai_manager")
        review_engine = MetadataReviewEngine(ai_manager)
        container.register_service("metadata_review_engine", review_engine)
        
        # INTEGRATION FIX: Bootstrapped Batch and Pipeline Integration services
        metadata_engine = container.get_service("metadata_engine")
        compliance_engine = container.get_service("compliance_engine")
        workspace_manager = container.get_service("workspace_manager")
        vision_engine = container.get_service("vision_engine")
        title_engine = container.get_service("title_engine")
        desc_engine = container.get_service("desc_engine")
        kw_engine = container.get_service("kw_engine")
        
        batch_manager = BatchManager(
            base_dir=AppConstants.BASE_DIR,
            ai_manager=ai_manager,
            metadata_engine=metadata_engine,
            review_engine=review_engine,
            compliance_engine=compliance_engine,
            workspace_manager=workspace_manager
        )
        container.register_service("batch_manager", batch_manager)
        
        integration_manager = PipelineIntegrationManager(
            ai_manager=ai_manager,
            vision_engine=vision_engine,
            title_engine=title_engine,
            desc_engine=desc_engine,
            kw_engine=kw_engine,
            review_engine=review_engine,
            compliance_engine=compliance_engine,
            workspace_manager=workspace_manager
        )
        container.register_service("integration_manager", integration_manager)
        
        return container