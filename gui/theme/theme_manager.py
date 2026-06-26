# gui/theme/theme_manager.py
import logging
from PySide6.QtWidgets import QApplication
from core.event_bus import EventBus
from core.constants import AppConstants
from gui.theme.palette import PaletteManager
from gui.theme.stylesheet import StylesheetManager

logger = logging.getLogger(__name__)

class UiThemeManager:
    """Orchestrates application-wide theme switching."""
    
    def __init__(self, app: QApplication, event_bus: EventBus) -> None:
        self.app = app
        self.event_bus = event_bus
        self._current_theme = "dark"
        self._registered_themes = ["dark", "light", "high_contrast"]
        
        # Subscribe to global theme change events
        self.event_bus.subscribe(AppConstants.EVENT_THEME_CHANGED, self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        """Internal handler for theme change events."""
        if theme_name != self._current_theme:
            self.apply_theme(theme_name)

    def apply_theme(self, theme_name: str) -> bool:
        """Applies a specified theme to the entire application instantly."""
        if theme_name not in self._registered_themes:
            logger.error(f"Attempted to apply unregistered theme: {theme_name}")
            return False

        self._current_theme = theme_name
        
        if theme_name == "dark":
            self.app.setPalette(PaletteManager.get_dark_palette())
        elif theme_name == "light":
            self.app.setPalette(PaletteManager.get_light_palette())
        elif theme_name == "high_contrast":
            self.app.setPalette(PaletteManager.get_high_contrast_palette())
            
        stylesheet = StylesheetManager.load_stylesheet(theme_name)
        if stylesheet:
            self.app.setStyleSheet(stylesheet)
            logger.info(f"Theme switched to: {theme_name}")
            return True
            
        return False

    def get_current_theme(self) -> str:
        """Returns the active theme identifier."""
        return self._current_theme