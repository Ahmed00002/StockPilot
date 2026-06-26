# ai/orchestration/orchestration_events.py
import logging
from typing import List, Callable, Any
from dataclasses import dataclass

from ai.models import AIRequest, AIResponse
from ai.request_context import RequestContext

logger = logging.getLogger("OrchestrationEvents")

class OrchestrationEventPublisher:
    """
    Pub/Sub event bus strictly for Orchestration lifecycle changes to decouple UI dashboards.
    """

    def __init__(self):
        self._listeners: dict[str, List[Callable]] = {
            "request_received": [],
            "provider_selected": [],
            "request_succeeded": [],
            "request_failed": [],
            "failover_triggered": []
        }

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type in self._listeners:
            self._listeners[event_type].append(callback)

    def publish_request_received(self, request: AIRequest, context: RequestContext) -> None:
        for cb in self._listeners["request_received"]:
            cb(request, context)

    def publish_provider_selected(self, provider_name: str, request: AIRequest) -> None:
        for cb in self._listeners["provider_selected"]:
            cb(provider_name, request)

    def publish_request_succeeded(self, response: AIResponse) -> None:
        for cb in self._listeners["request_succeeded"]:
            cb(response)

    def publish_request_failed(self, error: Exception, context: RequestContext) -> None:
        for cb in self._listeners["request_failed"]:
            cb(error, context)

    def publish_failover_triggered(self, failed_provider: str, error: Exception) -> None:
        for cb in self._listeners["failover_triggered"]:
            cb(failed_provider, error)