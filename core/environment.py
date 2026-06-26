# core/environment.py
import sys
import logging

logger = logging.getLogger(__name__)

class EnvironmentChecker:
    """Validates the runtime environment before application launch."""

    @staticmethod
    def check_python_version() -> None:
        """Ensures the application is running on Python 3.12 or newer."""
        required_major = 3
        required_minor = 12
        
        if sys.version_info < (required_major, required_minor):
            error_msg = f"StockPilot AI requires Python {required_major}.{required_minor} or higher. Current version: {sys.version}"
            logger.critical(error_msg)
            sys.exit(1)
        logger.info(f"Python version check passed: {sys.version.split()[0]}")