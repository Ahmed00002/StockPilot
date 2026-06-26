# ai/providers/groq_errors.py
import logging

logger = logging.getLogger("GroqErrors")

class GroqProviderError(Exception):
    """Base exception for all Groq Provider errors."""
    pass

class GroqAuthenticationError(GroqProviderError):
    """Raised when the Groq API key is invalid or unauthorized."""
    pass

class GroqRateLimitError(GroqProviderError):
    """Raised when Groq rate limits or quotas are exceeded."""
    pass

class GroqTimeoutError(GroqProviderError):
    """Raised when a Groq request times out."""
    pass

class GroqInvalidRequestError(GroqProviderError):
    """Raised when the request parameters or structure are malformed."""
    pass

class GroqCapabilityError(GroqProviderError):
    """Raised when requesting a capability (e.g., vision) not supported by the model."""
    pass

class GroqErrorMapper:
    """Maps official Groq SDK exceptions to internal application exceptions."""
    
    @staticmethod
    def map_exception(e: Exception) -> Exception:
        error_name = type(e).__name__
        error_msg = str(e)
        
        logger.debug(f"Mapping Groq exception: {error_name} - {error_msg}")
        
        if error_name == "AuthenticationError":
            return GroqAuthenticationError(f"Groq Authentication failed: {error_msg}")
        elif error_name == "RateLimitError":
            return GroqRateLimitError(f"Groq Rate limit exceeded: {error_msg}")
        elif error_name in ["APITimeoutError", "Timeout"]:
            return GroqTimeoutError(f"Groq request timed out: {error_msg}")
        elif error_name in ["BadRequestError", "InvalidRequestError"]:
            return GroqInvalidRequestError(f"Invalid Groq request parameters: {error_msg}")
        elif error_name == "APIConnectionError":
            return GroqProviderError(f"Groq Network/Connection error: {error_msg}")
            
        return GroqProviderError(f"Unexpected Groq API error: {error_msg}")