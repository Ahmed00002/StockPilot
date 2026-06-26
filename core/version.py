# core/version.py
from core.constants import AppConstants

class VersionManager:
    """Manages application versioning and compatibility checks."""

    @staticmethod
    def get_version() -> str:
        """Returns the current application version."""
        return AppConstants.APP_VERSION

    @staticmethod
    def is_compatible(required_version: str) -> bool:
        """Checks if a given version string is compatible with the current version."""
        current = list(map(int, AppConstants.APP_VERSION.split('.')))
        required = list(map(int, required_version.split('.')))
        return current >= required