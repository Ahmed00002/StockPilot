# ai/providers/openrouter_models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

@dataclass
class OpenRouterModelMeta:
    """Metadata tracking parameters for models discovered via OpenRouter endpoints."""
    id: str
    name: str
    provider: str
    context_length: int
    input_cost_per_token: float  # Absolute cost normalized to a single token unit
    output_cost_per_token: float
    supports_vision: bool = False
    supports_streaming: bool = False
    supports_json: bool = False
    supports_tools: bool = False
    supports_reasoning: bool = False
    is_active: bool = True
    last_updated: datetime = field(default_factory=datetime.now)