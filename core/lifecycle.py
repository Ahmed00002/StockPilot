# core/lifecycle.py
import logging
from core.dependency_container import DependencyContainer
from core.constants import AppConstants
from core.exceptions import InitializationError

logger = logging.getLogger(__name__)

class StartupManager:
    """Handles the sequential application startup process."""
    def __init__(self, container: DependencyContainer) -> None:
        self.container = container

    def execute(self) -> None:
        """Executes all startup routines."""
        logger.info("Executing startup sequence...")
        try:
            self.container.config_manager.load()
            self.container.event_bus.publish(AppConstants.EVENT_APP_STARTED)
            logger.info("Startup sequence complete.")
        except Exception as e:
            logger.critical(f"Startup failed: {e}")
            raise InitializationError(f"Startup sequence aborted due to error: {e}")

class ShutdownManager:
    """Handles graceful application termination."""
    def __init__(self, container: DependencyContainer) -> None:
        self.container = container

    def execute(self) -> None:
        """Executes all shutdown routines safely."""
        logger.info("Executing shutdown sequence...")
        try:
            self.container.event_bus.publish(AppConstants.EVENT_APP_SHUTDOWN)
            logger.info("Shutdown sequence complete.")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

class ApplicationLifecycleManager:
    """Coordinates the startup and shutdown phases."""
    def __init__(self, container: DependencyContainer) -> None:
        self.startup_manager = StartupManager(container)
        self.shutdown_manager = ShutdownManager(container)

    def start(self) -> None:
        """Initiates the application boot process."""
        self.startup_manager.execute()

    def stop(self) -> None:
        """Initiates the application teardown process."""
        self.shutdown_manager.execute()