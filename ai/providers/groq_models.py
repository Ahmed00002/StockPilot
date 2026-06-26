# ai/providers/groq_models.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class GroqGenerationConfig:
    """Encapsulates generation parameters formatted for Groq completions."""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    response_format: Optional[Dict[str, str]] = None
