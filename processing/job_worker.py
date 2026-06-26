# processing/job_worker.py
import logging
from typing import Callable, Any

from processing.batch_job import BatchJob
from processing.batch_pipeline import BatchPipeline
from processing.batch_context import BatchContext

logger = logging.getLogger(__name__)

class JobWorker:
    def __init__(self, pipeline: BatchPipeline, callback: Callable):
        self.pipeline = pipeline
        self.callback = callback

    def run(self, job: BatchJob) -> None:
        try:
            context = BatchContext(job=job)
            result = self.pipeline.execute(context)
            
            if result.success:
                self.callback(job, True, None)
            else:
                self.callback(job, False, result.error_message)
                
        except Exception as e:
            logger.exception(f"Unhandled exception in JobWorker for {job.job_id}")
            self.callback(job, False, str(e))