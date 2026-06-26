# ai/providers/deepseek_config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class DeepSeekConfig:
    """Configuration settings specific to the DeepSeek provider."""
    api_key: str = ""
    default_text_model: str = "deepseek-chat"
    default_reasoning_model: str = "deepseek-reasoner"
    supported_models: List[str] = field(default_factory=lambda: [
        "deepseek-chat",
        "deepseek-reasoner"
    ])
    timeout_seconds: int = 45
    max_retries: int = 3
    retry_delay_seconds: float = 2.0