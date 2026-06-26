# integration/metadata_pipeline_events.py
import logging
from typing import Callable, Dict, List, Any
from enum import Enum

logger = logging.getLogger(__name__)

class PipelineEvent(Enum):
    PIPELINE_START = "pipeline_start"
    PIPELINE_COMPLETE = "pipeline_complete"
    PIPELINE_ERROR = "pipeline_error"
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    STAGE_ERROR = "stage_error"
    AI_FALLBACK = "ai_fallback"
    CACHE_HIT = "cache_hit"
    RETRY_ATTEMPT = "retry_attempt"
    VALIDATION_FAILED = "validation_failed"
    HEALTH_CHECK_FAILED = "health_check_failed"

class PipelineEventManager:
    def __init__(self):
        self._listeners: Dict[PipelineEvent, List[Callable]] = {e: [] for e in PipelineEvent}

    def subscribe(self, event: PipelineEvent, callback: Callable) -> None:
        if callback not in self._listeners[event]:
            self._listeners[event].append(callback)

    def emit(self, event: PipelineEvent, **kwargs: Any) -> None:
        logger.debug(f"Emitting pipeline event: {event.name}")
        for callback in self._listeners[event]:
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in pipeline event listener for {event.name}: {e}", exc_info=True)