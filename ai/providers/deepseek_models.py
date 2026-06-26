# ai/providers/deepseek_models.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class DeepSeekGenerationConfig:
    """Encapsulates generation parameters specifically formatted for DeepSeek."""
    temperature: float = 1.0  # DeepSeek recommends 1.0 for chat, 0.0 for code/math
    max_tokens: int = 4096
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    response_format: Optional[Dict[str, str]] = None