# core/theme_manager.py
import logging
from core.event_bus import EventBus
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class ThemeManager:
    """Manages application visual themes."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._current_theme = "dark"

    def apply_theme(self, theme_name: str) -> None:
        """Applies a specified theme to the application."""
        self._current_theme = theme_name
        logger.info(f"Theme '{theme_name}' applied.")
        self._event_bus.publish(AppConstants.EVENT_THEME_CHANGED, theme_name)

    def get_current_theme(self) -> str:
        """Returns the name of the currently active theme."""
        return self._current_theme