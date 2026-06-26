# processing/resource_manager.py
import logging
from typing import Dict, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, max_cpu_percent: float = 90.0, max_ram_percent: float = 90.0):
        self.max_cpu_percent = max_cpu_percent
        self.max_ram_percent = max_ram_percent

    def get_system_stats(self) -> Dict[str, float]:
        if not HAS_PSUTIL:
            return {"cpu_percent": 0.0, "ram_percent": 0.0}
            
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent
        }

    def can_accept_job(self) -> bool:
        stats = self.get_system_stats()
        
        if stats["cpu_percent"] > self.max_cpu_percent:
            logger.warning("CPU usage too high. Throttling jobs.")
            return False
            
        if stats["ram_percent"] > self.max_ram_percent:
            logger.warning("RAM usage too high. Throttling jobs.")
            return False
            
        return True