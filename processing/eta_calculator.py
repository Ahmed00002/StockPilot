# processing/eta_calculator.py
import time
from collections import deque

class ETACalculator:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.completion_times = deque(maxlen=window_size)
        self.last_count = 0

    def calculate_eta(self, completed_count: int, remaining_count: int) -> tuple[float, float]:
        if remaining_count <= 0:
            return 0.0, 0.0
            
        current_time = time.time()
        
        if completed_count > self.last_count:
            self.completion_times.append(current_time)
            self.last_count = completed_count
            
        if len(self.completion_times) < 2:
            return -1.0, 0.0
            
        time_diff = self.completion_times[-1] - self.completion_times[0]
        jobs_diff = len(self.completion_times) - 1
        
        if time_diff <= 0:
            return -1.0, 0.0
            
        speed_jobs_per_sec = jobs_diff / time_diff
        eta_seconds = remaining_count / speed_jobs_per_sec if speed_jobs_per_sec > 0 else -1.0
        
        return eta_seconds, speed_jobs_per_sec