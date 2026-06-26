# ai/providers/openrouter_errors.py
import logging

logger = logging.getLogger("OpenRouterErrors")

class OpenRouterGatewayError(Exception):
    """Base exception for all OpenRouter AI Gateway errors."""
    pass

class OpenRouterAuthenticationError(OpenRouterGatewayError):
    """Raised when the OpenRouter API key is invalid or unauthorized."""
    pass

class OpenRouterRateLimitError(OpenRouterGatewayError):
    """Raised when OpenRouter gateway rate limits or account quotas are exceeded."""
    pass

class OpenRouterTimeoutError(OpenRouterGatewayError):
    """Raised when an OpenRouter upstream or gateway request times out."""
    pass

class OpenRouterInvalidRequestError(OpenRouterGatewayError):
    """Raised when the request parameters or structure are malformed."""
    pass

class OpenRouterModelUnavailableError(OpenRouterGatewayError):
    """Raised when the requested model is offline, deprecated, or unavailable via OpenRouter."""
    pass

class OpenRouterCapabilityError(OpenRouterGatewayError):
    """Raised when a specific model capability is requested but unsupported by that model."""
    pass

class OpenRouterErrorMapper:
    """Maps official OpenAI/OpenRouter error payloads or standard exceptions to internal exceptions."""
    
    @staticmethod
    def map_exception(e: Exception) -> Exception:
        error_name = type(e).__name__
        error_msg = str(e)
        
        logger.debug(f"Mapping OpenRouter exception: {error_name} - {error_msg}")
        
        if error_name == "AuthenticationError" or "401" in error_msg:
            return OpenRouterAuthenticationError(f"OpenRouter Authentication failed: {error_msg}")
        elif error_name == "RateLimitError" or "429" in error_msg:
            return OpenRouterRateLimitError(f"OpenRouter Rate limit or quota exceeded: {error_msg}")
        elif error_name in ["APITimeoutError", "Timeout"] or "504" in error_msg:
            return OpenRouterTimeoutError(f"OpenRouter request timed out: {error_msg}")
        elif "400" in error_msg or "BadRequestError" in error_name:
            return OpenRouterInvalidRequestError(f"Invalid OpenRouter request parameters: {error_msg}")
        elif "404" in error_msg or "NotFoundError" in error_name:
            return OpenRouterModelUnavailableError(f"Requested OpenRouter model is unavailable: {error_msg}")
        elif error_name == "APIConnectionError":
            return OpenRouterGatewayError(f"OpenRouter Gateway network connection error: {error_msg}")
            
        return OpenRouterGatewayError(f"Unexpected OpenRouter Gateway error: {error_msg}")