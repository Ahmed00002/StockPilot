# core/constants.py
import os
from pathlib import Path

class AppConstants:
    """Centralized application constants."""
    APP_NAME: str = "StockPilot AI"
    APP_VERSION: str = "1.0.0"
    
    BASE_DIR: Path = Path(__file__).parent.parent.resolve()
    CONFIG_DIR: Path = BASE_DIR / "config"
    LOGS_DIR: Path = BASE_DIR / "logs"
    WORKSPACES_DIR: Path = BASE_DIR / "workspaces"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    PLUGINS_DIR: Path = BASE_DIR / "plugins"
    EXPORTS_DIR: Path = BASE_DIR / "exports"
    CACHE_DIR: Path = BASE_DIR / "cache"
    
    APP_CONFIG_FILE: Path = CONFIG_DIR / "app_config.json"
    LOGGING_CONFIG_FILE: Path = CONFIG_DIR / "logging.json"
    
    EVENT_APP_STARTED: str = "app_started"
    EVENT_APP_SHUTDOWN: str = "app_shutdown"
    EVENT_WORKSPACE_LOADED: str = "workspace_loaded"
    EVENT_THEME_CHANGED: str = "theme_changed"