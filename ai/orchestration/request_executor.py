# ai/orchestration/request_executor.py
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable
import threading
import time

from ai.models import AIRequest, AIResponse
from ai.provider_manager import ProviderManager
from .request_queue import RequestQueue

logger = logging.getLogger("RequestExecutor")

class RequestExecutor:
    """
    Background worker pool executing AI requests asynchronously.
    De-couples network I/O from the GUI event loop.
    """

    def __init__(self, provider_manager: ProviderManager, request_queue: RequestQueue, max_workers: int = 4):
        self._provider_manager = provider_manager
        self._queue = request_queue
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _process_queue(self):
        """Continuous consumer loop pulling from the Priority Queue."""
        while self._running:
            if self._queue.is_paused():
                time.sleep(0.5)
                continue
                
            try:
                task = self._queue.get_next_task()
                
                if task.future.set_running_or_notify_cancel():
                    # Submit the actual execution to the thread pool
                    self._thread_pool.submit(self._execute_task_wrapper, task)
            except Exception as e:
                logger.error(f"Error pulling task from queue: {str(e)}")

    def _execute_task_wrapper(self, task):
        try:
            result = task.task_func()
            task.future.set_result(result)
        except Exception as e:
            task.future.set_exception(e)

    def submit_task(self, task_func: Callable) -> Future:
        """Schedules a pipeline function block for eventual execution."""
        return self._queue.schedule(task_func, priority=10)

    def execute_direct(self, provider_name: str, request: AIRequest) -> AIResponse:
        """
        Synchronous provider invocation called deep inside the worker threads.
        """
        provider = self._provider_manager.get_provider(provider_name)
        if not provider:
            raise RuntimeError(f"Executor failed: Provider '{provider_name}' not found or disabled.")
            
        if request.image_data:
            return provider.vision_request(request)
        return provider.text_request(request)

    def shutdown(self):
        self._running = False
        self._thread_pool.shutdown(wait=False)