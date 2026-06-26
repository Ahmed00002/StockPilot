# ai/orchestration/backoff_strategy.py
import math
import random
from dataclasses import dataclass
from typing import Literal

@dataclass
class BackoffConfig:
    strategy_type: Literal["linear", "exponential", "immediate"] = "exponential"
    base_delay_seconds: float = 2.0
    max_delay_seconds: float = 30.0
    jitter: bool = True

class BackoffStrategy:
    """
    Calculates dynamic sleep delays to prevent thundering herd problems during network outages.
    """

    def __init__(self, config: BackoffConfig = None):
        self.config = config or BackoffConfig()

    def calculate_delay(self, attempt_number: int) -> float:
        """
        Calculates the wait time for the specified attempt iteration.
        """
        if self.config.strategy_type == "immediate":
            return 0.0
            
        delay = 0.0
        
        if self.config.strategy_type == "linear":
            delay = self.config.base_delay_seconds * attempt_number
            
        elif self.config.strategy_type == "exponential":
            delay = self.config.base_delay_seconds * math.pow(2, attempt_number - 1)
            
        # Cap the delay to the configured maximum
        delay = min(delay, self.config.max_delay_seconds)
        
        # Apply full jitter if configured
        if self.config.jitter and delay > 0:
            delay = random.uniform(0, delay)
            
        return delay