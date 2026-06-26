# processing/batch_manager.py
import logging
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

from processing.batch_queue import BatchQueue
from processing.batch_scheduler import BatchScheduler
from processing.job_manager import JobManager
from processing.progress_tracker import ProgressTracker
from processing.processing_monitor import ProcessingMonitor
from processing.batch_history import BatchHistory
from processing.batch_statistics import BatchStatistics
from processing.job_recovery import JobRecovery
from processing.batch_job import BatchJob, JobState
from processing.resource_manager import ResourceManager
from processing.batch_events import BatchEventManager

logger = logging.getLogger(__name__)

class BatchManager:
    def __init__(self, base_dir: Path, ai_manager: Any, metadata_engine: Any, review_engine: Any, compliance_engine: Any, workspace_manager: Any):
        self.base_dir = base_dir
        self.events = BatchEventManager()
        self.queue = BatchQueue(self.events)
        self.progress = ProgressTracker(self.events)
        self.history = BatchHistory(base_dir / "batch_history")
        self.statistics = BatchStatistics(base_dir / "batch_stats.json")
        self.resource_manager = ResourceManager()
        self.monitor = ProcessingMonitor(self.progress, self.resource_manager)
        
        self.job_manager = JobManager(
            ai_manager=ai_manager,
            metadata_engine=metadata_engine,
            review_engine=review_engine,
            compliance_engine=compliance_engine,
            workspace_manager=workspace_manager,
            events=self.events
        )
        
        self.scheduler = BatchScheduler(
            queue=self.queue,
            job_manager=self.job_manager,
            resource_manager=self.resource_manager,
            progress=self.progress,
            events=self.events
        )
        
        self.recovery = JobRecovery(base_dir / "recovery", self.queue)
        logger.info("BatchManager initialized.")

    def start(self) -> None:
        self.recovery.recover_jobs()
        self.scheduler.start()
        logger.info("Batch processing started.")

    def stop(self) -> None:
        self.scheduler.stop()
        self.recovery.persist_queue()
        logger.info("Batch processing stopped.")

    def pause(self) -> None:
        self.scheduler.pause()
        logger.info("Batch processing paused.")

    def resume(self) -> None:
        self.scheduler.resume()
        logger.info("Batch processing resumed.")

    def add_job(self, image_path: str, priority: int = 1) -> str:
        job = self.queue.enqueue(image_path, priority)
        self.progress.add_job()
        self.recovery.save_job_state(job)
        return job.job_id

    def cancel_job(self, job_id: str) -> bool:
        return self.queue.cancel_job(job_id)

    def retry_job(self, job_id: str) -> bool:
        job = self.queue.get_job_by_id(job_id)
        if job and job.state in (JobState.FAILED, JobState.CANCELLED):
            self.queue.requeue(job_id)
            return True
        return False

    def clear_queue(self) -> None:
        self.queue.clear()
        self.progress.reset()
        self.recovery.clear_saved_states()