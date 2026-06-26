# ai/providers/openai_config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class OpenAIConfig:
    """Configuration settings specific to the OpenAI provider."""
    api_key: str = ""
    default_text_model: str = "gpt-4o-mini"
    default_vision_model: str = "gpt-4o"
    supported_models: List[str] = field(default_factory=lambda: [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ])
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 2.0