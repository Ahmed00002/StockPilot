# processing/job_result.py
from dataclasses import dataclass
from typing import Optional, Any
from processing.batch_context import BatchContext

@dataclass
class JobResult:
    success: bool
    context: BatchContext
    error_message: Optional[str] = None
    snapshot: Optional[Any] = None