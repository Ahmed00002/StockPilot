# integration/pipeline_diagnostics.py
import logging
from typing import Dict, Any

from integration.pipeline_health_monitor import PipelineHealthMonitor
from integration.dependency_checker import DependencyChecker
from integration.performance_profiler import PerformanceProfiler

logger = logging.getLogger(__name__)

class PipelineDiagnostics:
    def __init__(self, health_monitor: PipelineHealthMonitor, dep_checker: DependencyChecker, profiler: PerformanceProfiler):
        self.health = health_monitor
        self.deps = dep_checker
        self.profiler = profiler

    def run_full_diagnostics(self) -> Dict[str, Any]:
        logger.info("Running full pipeline diagnostics...")
        
        dep_ready, missing_deps = self.deps.check_dependencies()
        health_statuses = self.health.check_health()
        
        stages = ["vision", "title", "description", "keywords", "review", "compliance"]
        avg_durations = {s: self.profiler.get_average_stage_duration(s) for s in stages}
        
        is_healthy = dep_ready and all(s.is_healthy for s in health_statuses.values())
        
        report = {
            "status": "Healthy" if is_healthy else "Critical Issues",
            "dependencies_ok": dep_ready,
            "missing_dependencies": missing_deps,
            "health_checks": {k: {"healthy": v.is_healthy, "message": v.message} for k, v in health_statuses.items()},
            "performance_averages": avg_durations
        }
        
        if not is_healthy:
            logger.error("Pipeline diagnostics failed.")
        else:
            logger.info("Pipeline diagnostics passed successfully.")
            
        return report