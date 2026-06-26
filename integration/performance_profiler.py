# integration/performance_profiler.py
import time
import logging
from typing import Dict, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class StageProfile:
    stage_name: str
    start_time: float
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time

class PerformanceProfiler:
    def __init__(self):
        self.profiles: Dict[str, List[StageProfile]] = {}
        self.current_profiles: Dict[str, StageProfile] = {}

    def start_stage(self, job_id: str, stage_name: str) -> None:
        if job_id not in self.profiles:
            self.profiles[job_id] = []
            
        profile = StageProfile(stage_name=stage_name, start_time=time.time())
        self.current_profiles[f"{job_id}_{stage_name}"] = profile
        
    def end_stage(self, job_id: str, stage_name: str) -> None:
        key = f"{job_id}_{stage_name}"
        if key in self.current_profiles:
            profile = self.current_profiles.pop(key)
            profile.end_time = time.time()
            self.profiles[job_id].append(profile)
            logger.debug(f"Stage '{stage_name}' for job {job_id} took {profile.duration:.3f}s")

    def get_job_profile(self, job_id: str) -> List[StageProfile]:
        return self.profiles.get(job_id, [])

    def get_average_stage_duration(self, stage_name: str) -> float:
        durations = []
        for job_profiles in self.profiles.values():
            for p in job_profiles:
                if p.stage_name == stage_name and p.end_time > 0:
                    durations.append(p.duration)
        if not durations:
            return 0.0
        return sum(durations) / len(durations)

    def clear(self) -> None:
        self.profiles.clear()
        self.current_profiles.clear()