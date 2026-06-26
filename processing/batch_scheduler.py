# processing/batch_scheduler.py
import threading
import time
import logging
from typing import Any

from processing.batch_queue import BatchQueue
from processing.job_manager import JobManager
from processing.resource_manager import ResourceManager
from processing.progress_tracker import ProgressTracker
from processing.batch_events import BatchEventManager
from processing.batch_job import JobState

logger = logging.getLogger(__name__)

class BatchScheduler:
    def __init__(self, queue: BatchQueue, job_manager: JobManager, resource_manager: ResourceManager, progress: ProgressTracker, events: BatchEventManager):
        self.queue = queue
        self.job_manager = job_manager
        self.resource_manager = resource_manager
        self.progress = progress
        self.events = events
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: threading.Thread = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._pause_event.set()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="BatchSchedulerThread")
        self._thread.start()
        logger.info("BatchScheduler started.")

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("BatchScheduler stopped.")

    def pause(self) -> None:
        self._pause_event.clear()
        self.queue.pause()

    def resume(self) -> None:
        self._pause_event.set()
        self.queue.resume()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            self._pause_event.wait()
            
            if self._stop_event.is_set():
                break

            if not self.resource_manager.can_accept_job():
                time.sleep(1.0)
                continue

            if not self.job_manager.has_capacity():
                time.sleep(0.5)
                continue

            job = self.queue.dequeue()
            if job:
                job.started_at = time.time()
                self.queue.update_job_state(job.job_id, JobState.RUNNING)
                self.job_manager.submit_job(job)
            else:
                time.sleep(1.0)