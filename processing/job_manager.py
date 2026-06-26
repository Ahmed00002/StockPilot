# processing/job_manager.py
import logging
import time
from typing import Any, Dict

from processing.batch_job import BatchJob, JobState
from processing.batch_executor import BatchExecutor
from processing.batch_pipeline import BatchPipeline
from processing.batch_context import BatchContext
from processing.job_worker import JobWorker
from processing.batch_events import BatchEventManager
from processing.job_retry import JobRetryManager

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self, ai_manager: Any, metadata_engine: Any, review_engine: Any, compliance_engine: Any, workspace_manager: Any, events: BatchEventManager):
        self.events = events
        self.executor = BatchExecutor(max_workers=4)
        self.pipeline = BatchPipeline(ai_manager, metadata_engine, review_engine, compliance_engine, workspace_manager)
        self.retry_manager = JobRetryManager()
        self.active_jobs: Dict[str, BatchJob] = {}

    def has_capacity(self) -> bool:
        return self.executor.active_count < self.executor.max_workers

    def submit_job(self, job: BatchJob) -> None:
        self.active_jobs[job.job_id] = job
        self.events.emit_job_started(job)
        
        worker = JobWorker(self.pipeline, self._on_job_completed)
        self.executor.submit(job.job_id, worker.run, job)

    def _on_job_completed(self, job: BatchJob, success: bool, error: str = None) -> None:
        job.completed_at = time.time()
        
        if success:
            job.state = JobState.COMPLETED
            self.events.emit_job_completed(job)
        else:
            if self.retry_manager.should_retry(job):
                job.retry_count += 1
                job.state = JobState.RETRYING
                job.error_message = f"Retrying ({job.retry_count}/{job.max_retries}): {error}"
                self.events.emit_job_state_changed(job)
            else:
                job.state = JobState.FAILED
                job.error_message = error
                self.events.emit_job_failed(job)
                
        self.active_jobs.pop(job.job_id, None)

    def update_max_workers(self, workers: int) -> None:
        self.executor.max_workers = workers
        logger.info(f"Updated max workers to {workers}")