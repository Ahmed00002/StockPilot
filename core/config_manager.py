# core/config_manager.py
import json
import logging
from typing import Dict, Any
from core.constants import AppConstants
from core.exceptions import ConfigurationError

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages loading and saving of application configurations."""

    def __init__(self) -> None:
        self._config: Dict[str, Any] = {}

    def load(self) -> None:
        """Loads configuration from the default JSON file."""
        if not AppConstants.APP_CONFIG_FILE.exists():
            logger.warning("Configuration file not found. Using defaults.")
            self._config = {"debug_mode": False}
            return

        try:
            with open(AppConstants.APP_CONFIG_FILE, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info("Configuration loaded successfully.")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to read config file: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value by key."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Sets a configuration value and saves to disk."""
        self._config[key] = value
        self._save()

    def _save(self) -> None:
        """Writes the current configuration to disk."""
        try:
            with open(AppConstants.APP_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")