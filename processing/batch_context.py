# processing/batch_context.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from processing.batch_job import BatchJob

@dataclass
class BatchContext:
    job: BatchJob
    vision_data: Dict[str, Any] = field(default_factory=dict)
    metadata_package: Optional[Any] = None
    review_report: Optional[Any] = None
    compliance_report: Optional[Any] = None
    workspace_snapshot: Optional[Any] = None

    def set_vision_data(self, data: Dict[str, Any]) -> None:
        self.vision_data = data

    def set_metadata(self, metadata: Any) -> None:
        self.metadata_package = metadata

    def set_review_report(self, report: Any) -> None:
        self.review_report = report

    def set_compliance_report(self, report: Any) -> None:
        self.compliance_report = report