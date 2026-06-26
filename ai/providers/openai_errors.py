# ai/providers/openai_errors.py
import logging

logger = logging.getLogger("OpenAIErrors")

class OpenAIProviderError(Exception):
    """Base exception for all OpenAI Provider errors."""
    pass

class OpenAIAuthenticationError(OpenAIProviderError):
    """Raised when the OpenAI API key is invalid or unauthorized."""
    pass

class OpenAIRateLimitError(OpenAIProviderError):
    """Raised when OpenAI rate limits or quotas are exceeded."""
    pass

class OpenAITimeoutError(OpenAIProviderError):
    """Raised when an OpenAI request times out."""
    pass

class OpenAIInvalidRequestError(OpenAIProviderError):
    """Raised when the request parameters or structure are malformed."""
    pass

class OpenAIErrorMapper:
    """Maps official OpenAI SDK exceptions to internal application exceptions."""
    
    @staticmethod
    def map_exception(e: Exception) -> Exception:
        error_name = type(e).__name__
        error_msg = str(e)
        
        logger.debug(f"Mapping OpenAI exception: {error_name} - {error_msg}")
        
        if error_name == "AuthenticationError":
            return OpenAIAuthenticationError(f"OpenAI Authentication failed: {error_msg}")
        elif error_name == "RateLimitError":
            return OpenAIRateLimitError(f"OpenAI Rate limit or quota exceeded: {error_msg}")
        elif error_name in ["Timeout", "APITimeoutError"]:
            return OpenAITimeoutError(f"OpenAI request timed out: {error_msg}")
        elif error_name in ["BadRequestError", "InvalidRequestError"]:
            return OpenAIInvalidRequestError(f"Invalid OpenAI request parameters: {error_msg}")
        elif error_name == "APIConnectionError":
            return OpenAIProviderError(f"OpenAI Network/Connection error: {error_msg}")
            
        return OpenAIProviderError(f"Unexpected OpenAI API error: {error_msg}")