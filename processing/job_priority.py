# processing/job_priority.py
from enum import IntEnum

class JobPriority(IntEnum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0