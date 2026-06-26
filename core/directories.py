# core/directories.py
import logging
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class DirectoryInitializer:
    """Ensures all required application directories exist on startup."""

    @staticmethod
    def initialize() -> None:
        """Creates necessary directory structures if they do not exist."""
        directories = [
            AppConstants.LOGS_DIR,
            AppConstants.WORKSPACES_DIR,
            AppConstants.ASSETS_DIR,
            AppConstants.PLUGINS_DIR,
            AppConstants.CONFIG_DIR,
            AppConstants.EXPORTS_DIR,
            AppConstants.CACHE_DIR
        ]
        
        for directory in directories:
            if not directory.exists():
                try:
                    directory.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {directory}")
                except OSError as e:
                    logger.critical(f"Failed to create directory {directory}: {e}")
                    raise
        logger.info("Directory initialization complete.")