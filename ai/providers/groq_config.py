# ai/providers/groq_config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class GroqConfig:
    """Configuration settings specific to the Groq provider."""
    api_key: str = ""
    default_text_model: str = "llama3-70b-8192"
    default_vision_model: str = "llama-3.2-11b-vision-preview"
    supported_models: List[str] = field(default_factory=lambda: [
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma-7b-it",
        "gemma2-9b-it",
        "llama-3.2-11b-vision-preview",
        "llama-3.2-90b-vision-preview"
    ])
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 2.0