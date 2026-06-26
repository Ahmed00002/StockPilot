# processing/batch_events.py
import logging
from typing import Any, Callable, List, Dict
from processing.batch_job import BatchJob

logger = logging.getLogger(__name__)

class BatchEventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {
            "job_queued": [],
            "job_started": [],
            "job_completed": [],
            "job_failed": [],
            "job_state_changed": [],
            "queue_cleared": [],
            "progress_updated": []
        }

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].append(callback)

    def _emit(self, event_type: str, *args, **kwargs) -> None:
        for callback in self._listeners.get(event_type, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event listener for {event_type}: {e}")

    def emit_job_queued(self, job: BatchJob) -> None:
        self._emit("job_queued", job)

    def emit_job_started(self, job: BatchJob) -> None:
        self._emit("job_started", job)

    def emit_job_completed(self, job: BatchJob) -> None:
        self._emit("job_completed", job)

    def emit_job_failed(self, job: BatchJob) -> None:
        self._emit("job_failed", job)

    def emit_job_state_changed(self, job: BatchJob) -> None:
        self._emit("job_state_changed", job)

    def emit_queue_cleared(self) -> None:
        self._emit("queue_cleared")

    def emit_progress_updated(self, stats: Dict[str, Any]) -> None:
        self._emit("progress_updated", stats)
