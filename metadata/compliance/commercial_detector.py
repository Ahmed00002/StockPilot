# metadata/compliance/commercial_detector.py
import logging
from typing import List, Optional
from metadata.compliance.compliance_models import ComplianceIssue, Severity

logger = logging.getLogger(__name__)

class CommercialValueDetector:
    def __init__(self):
        self.strong_commercial = {"business", "corporate", "office", "design", "background", "technology", "modern", "concept"}

    def detect(self, keywords: List[str]) -> Optional[ComplianceIssue]:
        lower_kws = set(k.lower() for k in keywords)
        hits = len(lower_kws.intersection(self.strong_commercial))
        
        if hits == 0:
            return ComplianceIssue(
                category="Commercial",
                message="Low Commercial Indicator Words.",
                severity=Severity.INFO,
                explanation="Consider adding industry or concept-specific terms to increase commercial visibility.",
                actionable=True
            )
        return None
