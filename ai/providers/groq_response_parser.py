# ai/providers/groq_response_parser.py
import logging
from typing import Any
from ai.models import AIResponse, TokenUsage, CostEstimate

logger = logging.getLogger("GroqResponseParser")

class GroqResponseParser:
    """Normalizes unstructured runtime outputs directly returned from Groq endpoints into standard schema."""

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
                    warnings.append("The response was truncated due to max_tokens limit.")
            else:
                warnings.append("The returned Groq response package did not contain choices.")
        except Exception as e:
            logger.error(f"Structural variance discovered while dissecting Groq payloads: {str(e)}")
            warnings.append("Response extraction degraded gracefully due to payload structure anomalies.")

        token_usage = TokenUsage()
        if hasattr(raw_completion, "usage") and raw_completion.usage:
            token_usage = TokenUsage(
                prompt_tokens=getattr(raw_completion.usage, "prompt_tokens", 0),
                response_tokens=getattr(raw_completion.usage, "completion_tokens", 0),
                total_tokens=getattr(raw_completion.usage, "total_tokens", 0)
            )

        return AIResponse(
            content=content.strip(),
            provider_name="Groq",
            model_used=getattr(raw_completion, "model", "unknown"),
            token_usage=token_usage,
            cost_estimate=CostEstimate(currency="USD", amount=0.0),
            execution_time_ms=execution_time_ms,
            finish_reason=str(finish_reason),
            warnings=warnings
        )