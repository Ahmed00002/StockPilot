# ai/providers/gemini_response_parser.py
import logging
import time
from typing import Optional

from ai.models import AIResponse, TokenUsage, CostEstimate
import google.generativeai as genai

logger = logging.getLogger("GeminiResponseParser")

class GeminiResponseParser:
    """Parses raw Gemini responses into normalized AIResponse objects."""

    @staticmethod
    def parse(
        raw_response: genai.types.GenerateContentResponse, 
        model_name: str, 
        execution_time_ms: float
    ) -> AIResponse:
        
        content = ""
        warnings = []
        finish_reason = "unknown"

        try:
            if raw_response.candidates:
                candidate = raw_response.candidates[0]
                finish_reason = str(candidate.finish_reason.name) if hasattr(candidate.finish_reason, 'name') else str(candidate.finish_reason)
                
                if finish_reason == "SAFETY":
                    warnings.append("Response was blocked due to safety settings.")
                elif finish_reason == "MAX_TOKENS":
                    warnings.append("Response was truncated due to max_tokens limit.")
                    
                if candidate.content and candidate.content.parts:
                    content = candidate.content.parts[0].text
            elif raw_response.prompt_feedback:
                warnings.append(f"Prompt feedback block: {raw_response.prompt_feedback}")
            else:
                content = raw_response.text
        except Exception as e:
            logger.error(f"Error extracting text from Gemini response: {str(e)}")
            warnings.append("Failed to cleanly extract response text.")
            
        token_usage = GeminiResponseParser._extract_token_usage(raw_response)
        
        return AIResponse(
            content=content.strip(),
            provider_name="Gemini",
            model_used=model_name,
            token_usage=token_usage,
            cost_estimate=CostEstimate(), # Cost estimation handled separately or at manager level
            execution_time_ms=execution_time_ms,
            finish_reason=finish_reason,
            warnings=warnings
        )

    @staticmethod
    def _extract_token_usage(raw_response: genai.types.GenerateContentResponse) -> TokenUsage:
        prompt_tokens = 0
        response_tokens = 0
        total_tokens = 0
        
        if hasattr(raw_response, 'usage_metadata') and raw_response.usage_metadata:
            metadata = raw_response.usage_metadata
            prompt_tokens = getattr(metadata, 'prompt_token_count', 0)
            response_tokens = getattr(metadata, 'candidates_token_count', 0)
            total_tokens = getattr(metadata, 'total_token_count', 0)
            
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens
        )