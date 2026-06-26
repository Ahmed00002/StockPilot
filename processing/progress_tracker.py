# processing/progress_tracker.py
import logging
from typing import Dict, Any

from processing.batch_events import BatchEventManager
from processing.batch_job import BatchJob, JobState

logger = logging.getLogger(__name__)

class ProgressTracker:
    def __init__(self, events: BatchEventManager):
        self.events = events
        self.total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
        
        self.events.subscribe("job_completed", self._on_job_completed)
        self.events.subscribe("job_failed", self._on_job_failed)

    def add_job(self) -> None:
        self.total_jobs += 1
        self._emit_update()

    def _on_job_completed(self, job: BatchJob) -> None:
        self.completed_jobs += 1
        self._emit_update()

    def _on_job_failed(self, job: BatchJob) -> None:
        self.failed_jobs += 1
        self._emit_update()

    def reset(self) -> None:
        self.total_jobs = 0
        self.completed_jobs = 0
        self.failed_jobs = 0
        self._emit_update()

    def _emit_update(self) -> None:
        stats = {
            "total": self.total_jobs,
            "completed": self.completed_jobs,
            "failed": self.failed_jobs,
            "remaining": self.total_jobs - self.completed_jobs - self.failed_jobs,
            "success_rate": (self.completed_jobs / max(1, self.completed_jobs + self.failed_jobs)) * 100.0
        }
        self.events.emit_progress_updated(stats)