# ai/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass(frozen=True)
class TokenUsage:
    """Represents the token consumption for a single AI request."""
    prompt_tokens: int = 0
    response_tokens: int = 0
    total_tokens: int = 0

@dataclass(frozen=True)
class CostEstimate:
    """Represents the estimated financial cost of an AI request."""
    currency: str = "USD"
    amount: float = 0.0

@dataclass(frozen=True)
class HealthStatus:
    """Represents the operational health of an AI provider."""
    is_healthy: bool
    latency_ms: float
    last_checked: datetime
    error_message: Optional[str] = None

@dataclass(frozen=True)
class ProviderInformation:
    """Static and operational information about a specific AI provider."""
    name: str
    version: str
    supported_models: List[str]
    capabilities: List[str]

@dataclass
class AIRequest:
    """Encapsulates a normalized request to be sent to an AI provider."""
    prompt: str
    system_prompt: Optional[str] = None
    image_data: Optional[bytes] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout_seconds: int = 30
    additional_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIResponse:
    """Encapsulates a normalized response from an AI provider."""
    content: str
    provider_name: str
    model_used: str
    token_usage: TokenUsage
    cost_estimate: CostEstimate
    execution_time_ms: float
    finish_reason: str = "stop"
    warnings: List[str] = field(default_factory=list)