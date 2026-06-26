# processing/batch_queue.py
import threading
import logging
from queue import PriorityQueue
from typing import List, Optional, Dict

from processing.batch_job import BatchJob, JobState
from processing.batch_events import BatchEventManager

logger = logging.getLogger(__name__)

class BatchQueue:
    def __init__(self, events: BatchEventManager):
        self.events = events
        self._queue: PriorityQueue = PriorityQueue()
        self._jobs: Dict[str, BatchJob] = {}
        self._lock = threading.RLock()
        self._is_paused = False

    def enqueue(self, image_path: str, priority: int = 1) -> BatchJob:
        with self._lock:
            job = BatchJob(image_path=image_path, priority=priority, state=JobState.QUEUED)
            self._jobs[job.job_id] = job
            self._queue.put((priority, job.created_at, job.job_id))
            self.events.emit_job_queued(job)
            logger.debug(f"Enqueued job {job.job_id} for {image_path}")
            return job

    def requeue(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.state = JobState.QUEUED
                job.error_message = None
                self._queue.put((job.priority, job.created_at, job.job_id))
                self.events.emit_job_queued(job)
                logger.debug(f"Requeued job {job_id}")

    def restore_job(self, job: BatchJob) -> None:
        """Restores a persisted job into the queue for recovery."""
        with self._lock:
            job.state = JobState.QUEUED
            job.error_message = None
            self._jobs[job.job_id] = job
            self._queue.put((job.priority, job.created_at, job.job_id))
            self.events.emit_job_queued(job)
            logger.debug(f"Restored job {job.job_id} for {job.image_path}")

    def dequeue(self) -> Optional[BatchJob]:
        with self._lock:
            if self._is_paused or self._queue.empty():
                return None
                
            while not self._queue.empty():
                _, _, job_id = self._queue.get()
                job = self._jobs.get(job_id)
                if job and job.state == JobState.QUEUED:
                    return job
            return None

    def get_job_by_id(self, job_id: str) -> Optional[BatchJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def update_job_state(self, job_id: str, state: JobState, error: Optional[str] = None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.state = state
                if error:
                    job.error_message = error
                self.events.emit_job_state_changed(job)

    def cancel_job(self, job_id: str) -> bool:
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.state in (JobState.QUEUED, JobState.WAITING, JobState.PENDING):
                self.update_job_state(job_id, JobState.CANCELLED)
                return True
            return False

    def get_all_jobs(self) -> List[BatchJob]:
        with self._lock:
            return list(self._jobs.values())

    def clear(self) -> None:
        with self._lock:
            while not self._queue.empty():
                self._queue.get()
            self._jobs.clear()
            self.events.emit_queue_cleared()

    def pause(self) -> None:
        with self._lock:
            self._is_paused = True

    def resume(self) -> None:
        with self._lock:
            self._is_paused = False

    @property
    def size(self) -> int:
        with self._lock:
            return self._queue.qsize()
