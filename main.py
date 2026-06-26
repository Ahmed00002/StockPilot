# main.py
import sys
import logging
from PySide6.QtWidgets import QApplication
from core.bootstrap import ApplicationBootstrap
from gui.app import StockPilotApp

logger = logging.getLogger(__name__)

def global_exception_handler(exc_type, exc_value, exc_traceback) -> None:
    """Catches unhandled exceptions and logs them to prevent silent crashes."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught application exception:", exc_info=(exc_type, exc_value, exc_traceback))

def main() -> None:
    """Main application entry point."""
    # Register global exception handler for Qt event loop
    sys.excepthook = global_exception_handler
    
    # 1. Safely retrieve or instantiate QApplication
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    try:
        # 2. Bootstrap Core Environment & Services
        container = ApplicationBootstrap.run()
        logger.info("StockPilot AI core initialized successfully. Launching GUI...")
        
        # 3. Initialize and Execute GUI Application
        gui_app = StockPilotApp(app, container)
        exit_code = gui_app.execute()
        
        # 4. Graceful Shutdown
        lifecycle = container.get_service("lifecycle")
        if lifecycle:
            lifecycle.stop()
            
        sys.exit(exit_code)
        
    except Exception as e:
        logger.critical(f"Fatal application crash: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()