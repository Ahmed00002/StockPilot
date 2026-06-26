# integration/pipeline_health_monitor.py
import logging
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from integration.metadata_pipeline_events import PipelineEventManager, PipelineEvent

logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    is_healthy: bool
    component: str
    message: str
    timestamp: float = field(default_factory=time.time)

class PipelineHealthMonitor:
    def __init__(self, ai_manager: Any, vision_engine: Any, workspace_manager: Any, events: PipelineEventManager):
        self.ai = ai_manager
        self.vision = vision_engine
        self.workspace = workspace_manager
        self.events = events
        self.status_history: List[HealthStatus] = []

    def check_health(self) -> Dict[str, HealthStatus]:
        statuses = {}
        
        try:
            is_ai_healthy = self.ai.check_connection()
            msg = "AI connection established." if is_ai_healthy else "AI connection failed."
            statuses["ai_manager"] = HealthStatus(is_healthy=is_ai_healthy, component="AIManager", message=msg)
        except Exception as e:
            statuses["ai_manager"] = HealthStatus(is_healthy=False, component="AIManager", message=str(e))

        try:
            is_vision_ready = self.vision.is_ready()
            msg = "Vision models loaded." if is_vision_ready else "Vision models not loaded."
            statuses["vision_engine"] = HealthStatus(is_healthy=is_vision_ready, component="VisionEngine", message=msg)
        except Exception as e:
            statuses["vision_engine"] = HealthStatus(is_healthy=False, component="VisionEngine", message=str(e))

        try:
            workspace_dir = self.workspace.workspace_dir
            is_fs_healthy = workspace_dir.exists() and os.access(workspace_dir, os.W_OK)
            msg = "Workspace writable." if is_fs_healthy else "Workspace missing or read-only."
            statuses["workspace"] = HealthStatus(is_healthy=is_fs_healthy, component="Workspace", message=msg)
        except Exception as e:
            statuses["workspace"] = HealthStatus(is_healthy=False, component="Workspace", message=str(e))
            
        for status in statuses.values():
            self.status_history.append(status)
            if not status.is_healthy:
                self.events.emit(PipelineEvent.HEALTH_CHECK_FAILED, component=status.component, message=status.message)

        if len(self.status_history) > 100:
            self.status_history = self.status_history[-100:]

        return statuses
        
    def is_pipeline_healthy(self) -> bool:
        statuses = self.check_health()
        return all(s.is_healthy for s in statuses.values())