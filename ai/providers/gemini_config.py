# ai/providers/gemini_config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class GeminiConfig:
    """Configuration settings specific to the Google Gemini provider."""
    api_key: str = ""
    default_text_model: str = "gemini-1.5-pro"
    default_vision_model: str = "gemini-1.5-pro"
    supported_models: List[str] = field(default_factory=lambda: [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "gemini-1.0-pro-vision"
    ])
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 2.0