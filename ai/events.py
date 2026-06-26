# ai/events.py
from dataclasses import dataclass
from typing import Optional
from .models import HealthStatus, AIResponse

@dataclass(frozen=True)
class ProviderLoaded:
    """Event emitted when a provider is successfully loaded into the manager."""
    provider_name: str

@dataclass(frozen=True)
class ProviderUnloaded:
    """Event emitted when a provider is removed from the manager."""
    provider_name: str

@dataclass(frozen=True)
class ProviderFailed:
    """Event emitted when a provider fails a health check or a request critically."""
    provider_name: str
    error_message: str
    status: Optional[HealthStatus] = None

@dataclass(frozen=True)
class ProviderRecovered:
    """Event emitted when a previously failing provider passes a health check."""
    provider_name: str
    latency_ms: float

@dataclass(frozen=True)
class RequestStarted:
    """Event emitted when an AI request is dispatched to a provider."""
    request_id: str
    provider_name: str
    workspace: str

@dataclass(frozen=True)
class RequestFinished:
    """Event emitted when an AI request completes successfully."""
    request_id: str
    provider_name: str
    response: AIResponse

@dataclass(frozen=True)
class RequestCancelled:
    """Event emitted when an AI request is actively cancelled."""
    request_id: str
    provider_name: str
    reason: str