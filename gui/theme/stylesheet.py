# gui/theme/stylesheet.py
import logging
from pathlib import Path
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class StylesheetManager:
    """Manages loading and applying QSS files for themes."""

    @staticmethod
    def load_stylesheet(theme_name: str) -> str:
        """Reads a .qss file from the assets/themes directory."""
        theme_path: Path = AppConstants.ASSETS_DIR / "themes" / f"{theme_name}.qss"
        
        if not theme_path.exists():
            logger.warning(f"Theme file not found: {theme_path}. Returning empty stylesheet.")
            return ""
            
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load stylesheet {theme_name}: {e}")
            return ""