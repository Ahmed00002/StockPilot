# core/logger.py
import json
import logging
import logging.config
from core.constants import AppConstants

def setup_logging() -> None:
    """Initializes application logging based on the configuration file."""
    log_dir = AppConstants.LOGS_DIR
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)

    config_file = AppConstants.LOGGING_CONFIG_FILE
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.config.dictConfig(config)
            logging.getLogger(__name__).info("Logging configured from JSON.")
        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger(__name__).error(f"Failed to load logging config: {e}")
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        logging.getLogger(__name__).warning("Logging config file not found. Using basic configuration.")