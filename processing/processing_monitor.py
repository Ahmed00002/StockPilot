# processing/processing_monitor.py
import logging
from typing import Dict, Any

from processing.progress_tracker import ProgressTracker
from processing.resource_manager import ResourceManager
from processing.eta_calculator import ETACalculator

logger = logging.getLogger(__name__)

class ProcessingMonitor:
    def __init__(self, progress: ProgressTracker, resources: ResourceManager):
        self.progress = progress
        self.resources = resources
        self.eta_calc = ETACalculator()

    def get_monitor_data(self) -> Dict[str, Any]:
        stats = {
            "total": self.progress.total_jobs,
            "completed": self.progress.completed_jobs,
            "failed": self.progress.failed_jobs,
            "remaining": self.progress.total_jobs - self.progress.completed_jobs - self.progress.failed_jobs,
        }
        
        eta, speed = self.eta_calc.calculate_eta(stats["completed"], stats["remaining"])
        
        sys_stats = self.resources.get_system_stats()
        
        return {
            "progress": stats,
            "eta_seconds": eta,
            "speed_jobs_per_min": speed * 60,
            "cpu_usage": sys_stats.get("cpu_percent", 0.0),
            "ram_usage": sys_stats.get("ram_percent", 0.0)
        }