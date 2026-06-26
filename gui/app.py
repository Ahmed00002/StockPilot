# gui/app.py
import sys
import logging
import time
import json
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.theme.theme_manager import UiThemeManager
from gui.widgets.splash_screen import AppSplashScreen
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class StockPilotApp:
    """Bootstraps and manages the lifecycle of the PySide6 UI application."""

    def __init__(self, app: QApplication, container) -> None:
        self.app = app
        self.container = container
        
        self.app.setApplicationName(AppConstants.APP_NAME)
        self.app.setApplicationVersion(AppConstants.APP_VERSION)
        
        # Inject EventBus into UiThemeManager for reactive theme updates
        self.theme_manager = UiThemeManager(self.app, self.container.event_bus)
        
        # Load theme from config if available
        theme_to_load = "dark"
        ui_config_path = AppConstants.CONFIG_DIR / "ui_config.json"
        if ui_config_path.exists():
            try:
                with open(ui_config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                theme_to_load = cfg.get("theme", "dark")
            except Exception as e:
                logger.error(f"Failed to load UI config: {e}")
                
        # Apply theme via the Core Manager to synchronize global state and trigger event bus
        core_theme_manager = self.container.get_service("theme_manager")
        if core_theme_manager:
            core_theme_manager.apply_theme(theme_to_load)
        else:
            self.theme_manager.apply_theme(theme_to_load)
        
        self.splash = AppSplashScreen()
        self.main_window = None

    def execute(self) -> int:
        """Executes the PySide6 event loop."""
        self.splash.show()
        self.app.processEvents() # Force Qt to render the splash screen immediately
        
        self.splash.update_progress("Loading Core Modules...")
        self.app.processEvents()
        
        # Simulated loading delay for architecture modules
        time.sleep(0.5) 
        
        self.splash.update_progress("Initializing Main Window...")
        self.app.processEvents()
        
        # Inject the DependencyContainer into MainWindow
        self.main_window = MainWindow(self.container)
        
        self.splash.update_progress("Ready.")
        self.app.processEvents()
        time.sleep(0.2)
        
        self.main_window.show()
        self.splash.finish(self.main_window)
        
        logger.info("GUI event loop started.")
        return self.app.exec()