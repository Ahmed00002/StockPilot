# gui/widgets/icon_loader.py
import logging
from typing import Dict, Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class IconLoader:
    """Manages dynamic loading and caching of SVG/PNG icons."""
    
    _icon_cache: Dict[str, QIcon] = {}

    @classmethod
    def get_icon(cls, icon_name: str, color_mode: str = "default") -> QIcon:
        """
        Retrieves an icon from the assets folder.
        Uses caching to prevent disk I/O on repeated calls.
        """
        cache_key = f"{icon_name}_{color_mode}"
        if cache_key in cls._icon_cache:
            return cls._icon_cache[cache_key]

        icon_path = AppConstants.ASSETS_DIR / "icons" / f"{icon_name}.svg"
        
        if not icon_path.exists():
            icon_path = AppConstants.ASSETS_DIR / "icons" / f"{icon_name}.png"
            if not icon_path.exists():
                logger.debug(f"Icon not found: {icon_name}. Returning empty QIcon.")
                return QIcon()

        icon = QIcon(str(icon_path))
        cls._icon_cache[cache_key] = icon
        return icon

    @classmethod
    def clear_cache(cls) -> None:
        """Clears the icon cache, typically used during theme switching."""
        cls._icon_cache.clear()