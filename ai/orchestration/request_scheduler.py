# ai/orchestration/request_scheduler.py
import logging
import queue
from typing import Callable, Any
from dataclasses import dataclass
from concurrent.futures import Future

logger = logging.getLogger("RequestScheduler")

@dataclass
class ScheduledTask:
    priority: int
    task_func: Callable
    future: Future
    
    def __lt__(self, other):
        return self.priority < other.priority

class RequestScheduler:
    """
    Intelligent queuing mechanism supporting Priority, Normal, and Background tasks.
    Manages task dispatch limits.
    """

    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._is_paused = False

    def schedule(self, task_func: Callable, priority: int = 10) -> Future:
        """
        Priority levels: 1 (Highest/UI) to 100 (Lowest/Background).
        """
        future = Future()
        task = ScheduledTask(priority=priority, task_func=task_func, future=future)
        self._queue.put(task)
        logger.debug(f"Task scheduled with priority {priority}. Queue size: {self._queue.qsize()}")
        return future

    def get_next_task(self) -> ScheduledTask:
        return self._queue.get()

    def pause(self) -> None:
        self._is_paused = True
        logger.info("Request scheduler paused.")

    def resume(self) -> None:
        self._is_paused = False
        logger.info("Request scheduler resumed.")
        
    def is_paused(self) -> bool:
        return self._is_paused