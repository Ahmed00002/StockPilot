# ai/providers/deepseek_rate_limit.py
import time
import logging
from threading import Lock

logger = logging.getLogger("DeepSeekRateLimit")

class DeepSeekRateLimiter:
    """Manages rate limiting compliance and cooldown states for DeepSeek API endpoints."""
    
    def __init__(self, requests_per_minute: int = 200):
        self.requests_per_minute = requests_per_minute
        self._lock = Lock()
        self._timestamps: list[float] = []
        self._cooldown_expiry: float = 0.0
        
    def wait_if_needed(self) -> None:
        """Blocks execution synchronously if rate thresholds are active or saturated."""
        while True:
            sleep_duration = 0.0
            
            with self._lock:
                now = time.time()
                
                if now < self._cooldown_expiry:
                    sleep_duration = self._cooldown_expiry - now
                else:
                    self._timestamps = [ts for ts in self._timestamps if now - ts < 60.0]
                    
                    if len(self._timestamps) >= self.requests_per_minute:
                        sleep_duration = 60.0 - (now - self._timestamps[0])
                    else:
                        self._timestamps.append(time.time())
                        return
                        
            if sleep_duration > 0:
                logger.info(f"DeepSeek client pacing engaged. Delaying request by {sleep_duration:.2f}s.")
                time.sleep(sleep_duration)

    def enforce_cooldown(self, duration_seconds: float) -> None:
        """Enforces a sudden systemic timeout across matching provider executions."""
        with self._lock:
            self._cooldown_expiry = time.time() + duration_seconds
            logger.warning(f"DeepSeek rate limiter activated an explicit cooldown for {duration_seconds}s.")