# processing/job_retry.py
import logging
from processing.batch_job import BatchJob

logger = logging.getLogger(__name__)

class JobRetryManager:
    def __init__(self):
        self.unrecoverable_errors = [
            "File not found",
            "Invalid format",
            "API Key missing",
            "Quota exceeded"
        ]

    def should_retry(self, job: BatchJob) -> bool:
        if job.retry_count >= job.max_retries:
            logger.debug(f"Job {job.job_id} reached max retries.")
            return False
            
        if job.error_message:
            for unrecoverable in self.unrecoverable_errors:
                if unrecoverable.lower() in job.error_message.lower():
                    logger.debug(f"Job {job.job_id} encountered unrecoverable error.")
                    return False
                    
        return True