# ai/providers/gemini_errors.py
import logging

logger = logging.getLogger("GeminiErrors")

class GeminiProviderError(Exception):
    """Base exception for all Gemini Provider errors."""
    pass

class GeminiAuthenticationError(GeminiProviderError):
    """Raised when API key is invalid or unauthorized."""
    pass

class GeminiRateLimitError(GeminiProviderError):
    """Raised when provider rate limits are exceeded."""
    pass

class GeminiTimeoutError(GeminiProviderError):
    """Raised when a request exceeds the configured timeout."""
    pass

class GeminiInvalidRequestError(GeminiProviderError):
    """Raised when the request parameters or payload are invalid."""
    pass

class GeminiErrorMapper:
    """Maps Google SDK exceptions to application-specific exceptions."""
    
    @staticmethod
    def map_exception(e: Exception) -> Exception:
        error_name = type(e).__name__
        error_msg = str(e)
        
        logger.debug(f"Mapping Gemini exception: {error_name} - {error_msg}")
        
        if error_name == "InvalidArgument":
            return GeminiInvalidRequestError(f"Invalid request parameters: {error_msg}")
        elif error_name in ["PermissionDenied", "Unauthenticated"]:
            return GeminiAuthenticationError(f"Authentication failed. Check API key: {error_msg}")
        elif error_name == "ResourceExhausted":
            return GeminiRateLimitError(f"Rate limit or quota exceeded: {error_msg}")
        elif error_name == "DeadlineExceeded":
            return GeminiTimeoutError(f"Request timed out: {error_msg}")
        elif error_name == "InternalServerError":
            return GeminiProviderError(f"Internal Google server error: {error_msg}")
            
        return GeminiProviderError(f"Unexpected Gemini API error: {error_msg}")