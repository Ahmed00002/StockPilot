# ai/providers/gemini_request_builder.py
import io
import logging
from typing import List, Any
from PIL import Image

import google.generativeai as genai
from ai.models import AIRequest
from .gemini_models import GeminiGenerationConfig, GeminiSafetySettings

logger = logging.getLogger("GeminiRequestBuilder")

class GeminiRequestBuilder:
    """Constructs valid Gemini API payloads from internal AIRequest objects."""

    @staticmethod
    def build_generation_config(request: AIRequest) -> genai.types.GenerationConfig:
        config = GeminiGenerationConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        )
        return genai.types.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=config.top_p,
            top_k=config.top_k,
            candidate_count=config.candidate_count
        )

    @staticmethod
    def build_safety_settings() -> dict:
        return GeminiSafetySettings().to_dict()

    @staticmethod
    def build_text_content(request: AIRequest) -> List[Any]:
        content = []
        if request.system_prompt:
            content.append(f"System: {request.system_prompt}")
        content.append(request.prompt)
        return content

    @staticmethod
    def build_vision_content(request: AIRequest) -> List[Any]:
        content = GeminiRequestBuilder.build_text_content(request)
        
        if request.image_data:
            try:
                img = Image.open(io.BytesIO(request.image_data))
                # Ensure the image is in a compatible format
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                content.append(img)
            except Exception as e:
                logger.error(f"Failed to process image data for Gemini request: {str(e)}")
                raise ValueError("Invalid image data provided to Gemini vision request.") from e
                
        return content