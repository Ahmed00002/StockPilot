# gui/widgets/splash_screen.py
import logging
from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class AppSplashScreen(QSplashScreen):
    """Professional startup splash screen with message reporting."""

    def __init__(self) -> None:
        pixmap = self._generate_splash_pixmap()
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.showMessage(f"Starting {AppConstants.APP_NAME} v{AppConstants.APP_VERSION}...", 
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                         QColor(255, 255, 255))
        logger.info("Splash screen initialized.")

    def _generate_splash_pixmap(self) -> QPixmap:
        """Generates a default dark-mode pixmap if no logo asset exists."""
        logo_path = AppConstants.ASSETS_DIR / "logos" / "splash.png"
        if logo_path.exists():
            return QPixmap(str(logo_path))
            
        pixmap = QPixmap(600, 350)
        pixmap.fill(QColor(30, 30, 30))
        return pixmap

    def update_progress(self, message: str) -> None:
        """Updates the status text on the splash screen."""
        self.showMessage(message, 
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, 
                         QColor(204, 204, 204))
        self.repaint()
        logger.debug(f"Startup progress: {message}")