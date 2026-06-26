# core/event_bus.py
from typing import Callable, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """Synchronous event bus for decoupled component communication."""
    
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[..., None]]] = {}

    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        """Registers a callback for a specific event."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        if callback not in self._subscribers[event_name]:
            self._subscribers[event_name].append(callback)
            logger.debug(f"Subscribed to event: {event_name}")

    def unsubscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        """Removes a callback from a specific event."""
        if event_name in self._subscribers and callback in self._subscribers[event_name]:
            self._subscribers[event_name].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_name}")

    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Executes all callbacks registered to the given event."""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing callback for event '{event_name}': {e}")
        else:
            logger.debug(f"Event published with no subscribers: {event_name}")