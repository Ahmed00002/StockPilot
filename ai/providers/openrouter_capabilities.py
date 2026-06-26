# ai/providers/openrouter_capabilities.py
from dataclasses import dataclass
from typing import Optional
from .openrouter_models import OpenRouterModelMeta

@dataclass
class OpenRouterCapabilities:
    """Evaluates and matches real-time operational boundaries and features for specific models."""

    @staticmethod
    def verify_capability(model_meta: OpenRouterModelMeta, capability_name: str) -> bool:
        """Returns truth values regarding explicit capability presence within model metadata profiles."""
        name = capability_name.lower().strip()
        if name in ("vision", "image_input", "multimodal"):
            return model_meta.supports_vision
        elif name in ("streaming", "stream"):
            return model_meta.supports_streaming
        elif name in ("json", "structured_json", "json_output"):
            return model_meta.supports_json
        elif name in ("tools", "tool_calling", "function_calling"):
            return model_meta.supports_tools
        elif name in ("reasoning", "reasoner"):
            return model_meta.supports_reasoning
        elif name == "long_context":
            return model_meta.context_length >= 32768
        return False