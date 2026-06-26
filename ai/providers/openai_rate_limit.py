# ai/providers/openai_rate_limit.py
import time
import logging
from threading import Lock

logger = logging.getLogger("OpenAIRateLimit")

class OpenAIRateLimiter:
    """Manages rate limiting compliance and forced cool-down states for OpenAI endpoints."""
    
    def __init__(self, requests_per_minute: int = 500):
        self.requests_per_minute = requests_per_minute
        self._lock = Lock()
        self._timestamps: list[float] = []
        self._cooldown_expiry: float = 0.0
        
    def wait_if_needed(self) -> None:
        """
        Blocks execution synchronously if rate thresholds are active or saturated.
        Thread-safe execution ensures we don't sleep inside the lock, preventing starvation.
        """
        while True:
            sleep_duration = 0.0
            
            with self._lock:
                now = time.time()
                
                if now < self._cooldown_expiry:
                    # Enforced cooldown is active
                    sleep_duration = self._cooldown_expiry - now
                else:
                    # Clean up old timestamps
                    self._timestamps = [ts for ts in self._timestamps if now - ts < 60.0]
                    
                    if len(self._timestamps) >= self.requests_per_minute:
                        # Rate limit reached, calculate time until the oldest request clears
                        sleep_duration = 60.0 - (now - self._timestamps[0])
                    else:
                        # Safe to proceed; record current time and exit loop
                        self._timestamps.append(time.time())
                        return
                        
            # Sleep outside the lock to allow other threads to evaluate or record
            if sleep_duration > 0:
                logger.info(f"OpenAI client pacing engaged. Delaying request by {sleep_duration:.2f}s.")
                time.sleep(sleep_duration)

    def enforce_cooldown(self, duration_seconds: float) -> None:
        """Enforces a sudden systemic timeout across matching provider executions."""
        with self._lock:
            self._cooldown_expiry = time.time() + duration_seconds
            logger.warning(f"OpenAI rate limiter activated an explicit structural cooldown for {duration_seconds}s.")