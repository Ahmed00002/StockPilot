# ai/providers/deepseek_errors.py
import logging

logger = logging.getLogger("DeepSeekErrors")

class DeepSeekProviderError(Exception):
    """Base exception for all DeepSeek Provider errors."""
    pass

class DeepSeekAuthenticationError(DeepSeekProviderError):
    """Raised when the DeepSeek API key is invalid or unauthorized."""
    pass

class DeepSeekRateLimitError(DeepSeekProviderError):
    """Raised when DeepSeek rate limits or quotas are exceeded."""
    pass

class DeepSeekTimeoutError(DeepSeekProviderError):
    """Raised when a DeepSeek request times out."""
    pass

class DeepSeekInvalidRequestError(DeepSeekProviderError):
    """Raised when the request parameters or structure are malformed."""
    pass

class DeepSeekCapabilityError(DeepSeekProviderError):
    """Raised when requesting a capability not supported by the active model."""
    pass

class DeepSeekErrorMapper:
    """Maps official DeepSeek SDK/OpenAI-compatible exceptions to internal application exceptions."""
    
    @staticmethod
    def map_exception(e: Exception) -> Exception:
        error_name = type(e).__name__
        error_msg = str(e)
        
        logger.debug(f"Mapping DeepSeek exception: {error_name} - {error_msg}")
        
        if error_name == "AuthenticationError":
            return DeepSeekAuthenticationError(f"DeepSeek Authentication failed: {error_msg}")
        elif error_name == "RateLimitError":
            return DeepSeekRateLimitError(f"DeepSeek Rate limit exceeded: {error_msg}")
        elif error_name in ["APITimeoutError", "Timeout"]:
            return DeepSeekTimeoutError(f"DeepSeek request timed out: {error_msg}")
        elif error_name in ["BadRequestError", "InvalidRequestError"]:
            return DeepSeekInvalidRequestError(f"Invalid DeepSeek request parameters: {error_msg}")
        elif error_name == "APIConnectionError":
            return DeepSeekProviderError(f"DeepSeek Network/Connection error: {error_msg}")
            
        return DeepSeekProviderError(f"Unexpected DeepSeek API error: {error_msg}")