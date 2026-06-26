# ai/providers/gemini_models.py
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class GeminiGenerationConfig:
    """Encapsulates generation parameters for the Gemini API."""
    temperature: float = 0.7
    max_output_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40
    candidate_count: int = 1

@dataclass
class GeminiSafetySettings:
    """Defines content filtering thresholds for Gemini."""
    harassment: str = "BLOCK_MEDIUM_AND_ABOVE"
    hate_speech: str = "BLOCK_MEDIUM_AND_ABOVE"
    sexually_explicit: str = "BLOCK_MEDIUM_AND_ABOVE"
    dangerous_content: str = "BLOCK_MEDIUM_AND_ABOVE"

    def to_dict(self) -> Dict[str, str]:
        return {
            "HARM_CATEGORY_HARASSMENT": self.harassment,
            "HARM_CATEGORY_HATE_SPEECH": self.hate_speech,
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": self.sexually_explicit,
            "HARM_CATEGORY_DANGEROUS_CONTENT": self.dangerous_content,
        }