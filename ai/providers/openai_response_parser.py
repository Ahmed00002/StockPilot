# ai/providers/openai_response_parser.py
import logging
from typing import Any
from ai.models import AIResponse, TokenUsage, CostEstimate

logger = logging.getLogger("OpenAIResponseParser")

class OpenAIResponseParser:
    """Normalizes unstructured runtime outputs directly returned from OpenAI SDK endpoints into common schema definitions."""

    @staticmethod
    def parse(raw_completion: Any, execution_time_ms: float) -> AIResponse:
        """Transforms a raw ChatCompletion message into an application-safe AIResponse instance."""
        content = ""
        finish_reason = "unknown"
        warnings = []

        try:
            if raw_completion.choices:
                choice = raw_completion.choices[0]
                finish_reason = getattr(choice, "finish_reason", "unknown")
                if hasattr(choice, "message") and choice.message.content:
                    content = choice.message.content
                
                if finish_reason == "length":
                    warnings.append("The response sequence reached structural bounds and was truncated.")
                elif finish_reason == "content_filter":
                    warnings.append("System alerts: Content generation modified by active protective safety layers.")
            else:
                warnings.append("The returned OpenAI response package did not contain choices.")
        except Exception as e:
            logger.error(f"Structural variance discovered while dissecting OpenAI body payloads: {str(e)}")
            warnings.append("Response translation degraded gracefully during internal payload unboxing.")

        token_usage = TokenUsage()
        if hasattr(raw_completion, "usage") and raw_completion.usage:
            token_usage = TokenUsage(
                prompt_tokens=getattr(raw_completion.usage, "prompt_tokens", 0),
                response_tokens=getattr(raw_completion.usage, "completion_tokens", 0),
                total_tokens=getattr(raw_completion.usage, "total_tokens", 0)
            )

        return AIResponse(
            content=content.strip(),
            provider_name="OpenAI",
            model_used=getattr(raw_completion, "model", "unknown"),
            token_usage=token_usage,
            cost_estimate=CostEstimate(currency="USD", amount=0.0),
            execution_time_ms=execution_time_ms,
            finish_reason=str(finish_reason),
            warnings=warnings
        )