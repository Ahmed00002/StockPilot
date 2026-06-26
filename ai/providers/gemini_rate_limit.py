# ai/providers/gemini_rate_limit.py
import time
import logging
from threading import Lock

logger = logging.getLogger("GeminiRateLimit")

class GeminiRateLimiter:
    """Manages rate limits, cooldowns, and request tracking for the Gemini provider."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._lock = Lock()
        self._request_timestamps: list[float] = []
        self._cooldown_until: float = 0.0
        
    def wait_if_needed(self) -> None:
        """Blocks execution if the rate limit is reached or in a cooldown period."""
        with self._lock:
            current_time = time.time()
            
            if current_time < self._cooldown_until:
                sleep_time = self._cooldown_until - current_time
                logger.warning(f"Rate limit cooldown active. Sleeping for {sleep_time:.2f} seconds.")
                time.sleep(sleep_time)
                current_time = time.time()
                
            # Clean up old timestamps (older than 60 seconds)
            self._request_timestamps = [
                ts for ts in self._request_timestamps 
                if current_time - ts < 60.0
            ]
            
            if len(self._request_timestamps) >= self.requests_per_minute:
                oldest_timestamp = self._request_timestamps[0]
                sleep_time = 60.0 - (current_time - oldest_timestamp)
                if sleep_time > 0:
                    logger.info(f"Rate limit approaching. Pacing request by sleeping {sleep_time:.2f} seconds.")
                    time.sleep(sleep_time)
            
            self._request_timestamps.append(time.time())

    def trigger_cooldown(self, seconds: float) -> None:
        """Triggers a forced cooldown period (e.g., after a ResourceExhausted error)."""
        with self._lock:
            self._cooldown_until = time.time() + seconds
            logger.warning(f"Forced cooldown triggered for {seconds} seconds.")