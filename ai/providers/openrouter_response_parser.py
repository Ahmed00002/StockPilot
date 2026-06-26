# ai/providers/openrouter_response_parser.py
import logging
from typing import Any
from ai.models import AIResponse, TokenUsage, CostEstimate
from .openrouter_models import OpenRouterModelMeta

logger = logging.getLogger("OpenRouterResponseParser")

class OpenRouterResponseParser:
    """Normalizes arbitrary tracking data shapes extracted out of standard OpenRouter endpoint signals."""

    @staticmethod
    def parse(raw_completion: Any, model_meta: OpenRouterModelMeta, execution_time_ms: float) -> AIResponse:
        content = ""
        finish_reason = "unknown"
        warnings = []

        try:
            if hasattr(raw_completion, "choices") and raw_completion.choices:
                choice = raw_completion.choices[0]
                finish_reason = getattr(choice, "finish_reason", "unknown")
                if hasattr(choice, "message") and choice.message.content:
                    content = choice.message.content
                if finish_reason == "length":
                    warnings.append("Execution boundaries intercepted by configured token length ceilings.")
            else:
                warnings.append("OpenRouter response package arrived devoid of actionable message structures.")
        except Exception as e:
            logger.error(f"Error parsing OpenRouter response: {str(e)}")
            warnings.append("Partial payload validation exception recovered.")

        token_usage = TokenUsage()
        estimated_cost = 0.0

        if hasattr(raw_completion, "usage") and raw_completion.usage:
            prompt_tokens = getattr(raw_completion.usage, "prompt_tokens", 0)
            completion_tokens = getattr(raw_completion.usage, "completion_tokens", 0)
            total_tokens = getattr(raw_completion.usage, "total_tokens", 0)
            
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                response_tokens=completion_tokens,
                total_tokens=total_tokens
            )
            
            # Calculate pricing dynamically based on model registry metadata values
            estimated_cost = (prompt_tokens * model_meta.input_cost_per_token) + (completion_tokens * model_meta.output_cost_per_token)

        return AIResponse(
            content=content.strip(),
            provider_name=f"OpenRouter ({model_meta.provider})",
            model_used=model_meta.id,
            token_usage=token_usage,
            cost_estimate=CostEstimate(currency="USD", amount=estimated_cost),
            execution_time_ms=execution_time_ms,
            finish_reason=str(finish_reason),
            warnings=warnings
        )