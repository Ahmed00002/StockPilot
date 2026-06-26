# ai/providers/openai_models.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class OpenAIGenerationConfig:
    """Encapsulates generation parameters specifically formatted for OpenAI completions."""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    response_format: Optional[Dict[str, str]] = None

@dataclass
class OpenAIResponseMetadata:
    """Holds system-level execution metadata from an OpenAI response choice."""
    finish_reason: str
    system_fingerprint: Optional[str] = None