# ai/orchestration/retry_manager.py
import logging
import time
from typing import Callable, Any

from ai.models import AIRequest, AIResponse
from .backoff_strategy import BackoffStrategy

logger = logging.getLogger("RetryManager")

class RetryManager:
    """
    Evaluates operational exceptions during provider execution to determine if requests
    should be retried, managing the loop and delegating delay calculations to the BackoffStrategy.
    """

    def __init__(self, backoff_strategy: BackoffStrategy, max_retries: int = 3):
        self._backoff = backoff_strategy
        self._max_retries = max_retries

    def _is_recoverable(self, exception: Exception) -> bool:
        """Determines if an error type warrants a retry attempt."""
        error_name = type(exception).__name__
        error_msg = str(exception).lower()
        
        # Unrecoverable errors
        if "auth" in error_name.lower() or "auth" in error_msg or "credential" in error_msg:
            return False
        if "invalidrequest" in error_name.lower() or "malformed" in error_msg:
            return False
        if "capability" in error_name.lower():
            return False
            
        # Recoverable errors
        if "timeout" in error_name.lower():
            return True
        if "ratelimit" in error_name.lower() or "429" in error_msg:
            return True
        if "network" in error_name.lower() or "connection" in error_name.lower():
            return True
            
        # Default to False to prevent infinite looping on unknown fatal errors
        return False

    def execute_with_retries(
        self, 
        provider_name: str, 
        request: AIRequest, 
        executor_func: Callable[[str, AIRequest], AIResponse]
    ) -> AIResponse:
        
        last_exception = None
        
        for attempt in range(1, self._max_retries + 1):
            try:
                return executor_func(provider_name, request)
                
            except Exception as e:
                last_exception = e
                
                if not self._is_recoverable(e):
                    logger.warning(f"Unrecoverable error encountered for {provider_name}: {str(e)}")
                    raise e
                    
                if attempt == self._max_retries:
                    logger.error(f"Exhausted {self._max_retries} retries for provider {provider_name}.")
                    break
                    
                delay = self._backoff.calculate_delay(attempt)
                logger.info(f"Retry attempt {attempt}/{self._max_retries} for {provider_name} in {delay:.2f}s due to: {str(e)}")
                time.sleep(delay)
                
        raise last_exception