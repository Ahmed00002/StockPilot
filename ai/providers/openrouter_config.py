# ai/providers/openrouter_config.py
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class OpenRouterConfig:
    """Configuration settings specific to the OpenRouter AI Gateway."""
    api_key: str = ""
    default_model: str = "google/gemini-2.5-flash"
    fallback_model: str = "openai/gpt-4o-mini"
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    cache_ttl_seconds: int = 3600
    pinned_models: List[str] = field(default_factory=lambda: [
        "google/gemini-2.5-flash",
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
        "deepseek/deepseek-chat"
    ])
    disabled_models: List[str] = field(default_factory=list)
    favorite_models: List[str] = field(default_factory=list)
    routing_preference: str = "manual"  # choices: manual, cheapest, fastest, highest_context