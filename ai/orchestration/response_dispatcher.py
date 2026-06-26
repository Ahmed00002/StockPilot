# ai/orchestration/response_dispatcher.py
import logging
from typing import List, Callable

from ai.models import AIResponse
from ai.request_context import RequestContext

logger = logging.getLogger("ResponseDispatcher")

class ResponseDispatcher:
    """
    Subsystem responsible for taking final, normalized AIResponse objects and pushing
    them outwards to subscribing domains (SEO, Metadata Engine, History tracking).
    """

    def __init__(self):
        self._subscribers: List[Callable[[AIResponse, RequestContext], None]] = []

    def subscribe(self, callback: Callable[[AIResponse, RequestContext], None]) -> None:
        self._subscribers.append(callback)

    def dispatch(self, response: AIResponse, context: RequestContext) -> None:
        """Broadcasts the successful payload."""
        logger.debug(f"Dispatching AIResponse from {response.provider_name} to {len(self._subscribers)} subsystems.")
        for callback in self._subscribers:
            try:
                callback(response, context)
            except Exception as e:
                logger.error(f"Error in response subscriber callback: {str(e)}")