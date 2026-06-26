# processing/job_recovery.py
import json
import logging
from pathlib import Path
from typing import List

from processing.batch_job import BatchJob, JobState
from processing.batch_queue import BatchQueue

logger = logging.getLogger(__name__)

class JobRecovery:
    def __init__(self, recovery_dir: Path, queue: BatchQueue):
        self.recovery_dir = recovery_dir
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        self.queue = queue
        self.state_file = self.recovery_dir / "queue_state.json"

    def save_job_state(self, job: BatchJob) -> None:
        self.persist_queue()

    def persist_queue(self) -> None:
        jobs = self.queue.get_all_jobs()
        serializable_jobs = [j.to_dict() for j in jobs if j.state in (JobState.QUEUED, JobState.PENDING, JobState.WAITING, JobState.RUNNING)]
        
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_jobs, f, indent=2)
            logger.info(f"Persisted {len(serializable_jobs)} jobs for recovery.")
        except IOError as e:
            logger.error(f"Failed to persist queue state: {e}")

    def recover_jobs(self) -> None:
        if not self.state_file.exists():
            return
            
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            recovered_count = 0
            for job_data in data:
                job = BatchJob.from_dict(job_data)
                self.queue.restore_job(job)
                recovered_count += 1
                
            logger.info(f"Recovered {recovered_count} jobs from previous session.")
            self.state_file.unlink()
            
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to recover jobs: {e}")

    def clear_saved_states(self) -> None:
        if self.state_file.exists():
            self.state_file.unlink()
