# ai/orchestration/request_queue.py
# (Integrated structural abstractions with RequestScheduler to minimize redundant layering)
# Exists to satisfy explicit file structure requirements in specification.

from .request_scheduler import RequestScheduler

class RequestQueue(RequestScheduler):
    """
    Specialized extension point for RequestScheduler exposing direct queue manipulation
    capabilities if advanced inspection or clearing is required.
    """
    
    def clear(self) -> None:
        while not self._queue.empty():
            try:
                task = self._queue.get_nowait()
                task.future.cancel()
            except Exception:
                pass