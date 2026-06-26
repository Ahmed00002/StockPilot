# processing/batch_executor.py
import concurrent.futures
import logging
import threading
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)

class BatchExecutor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="BatchWorker"
        )
        self._futures: Dict[str, concurrent.futures.Future] = {}
        self._lock = threading.Lock()

    def submit(self, job_id: str, func: Callable, *args, **kwargs) -> None:
        with self._lock:
            future = self.executor.submit(func, *args, **kwargs)
            self._futures[job_id] = future
            future.add_done_callback(lambda f: self._on_done(job_id))

    def _on_done(self, job_id: str) -> None:
        with self._lock:
            self._futures.pop(job_id, None)

    def cancel(self, job_id: str) -> bool:
        with self._lock:
            future = self._futures.get(job_id)
            if future:
                return future.cancel()
            return False

    def shutdown(self, wait: bool = True) -> None:
        self.executor.shutdown(wait=wait)

    @property
    def active_count(self) -> int:
        with self._lock:
            return len(self._futures)