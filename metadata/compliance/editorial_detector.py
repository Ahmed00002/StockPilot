# metadata/compliance/editorial_detector.py
import logging
from typing import Optional, List
from metadata.compliance.compliance_models import ComplianceIssue, Severity

logger = logging.getLogger(__name__)

class EditorialDetector:
    def __init__(self):
        self.editorial_triggers = {
            "news", "event", "protest", "concert", "celebrity", 
            "politician", "sports match", "editorial", "documentary"
        }

    def detect(self, title: str, description: str, keywords: List[str]) -> Optional[ComplianceIssue]:
        text = f"{title} {description} {' '.join(keywords)}".lower()
        
        for trigger in self.editorial_triggers:
            if trigger in text:
                return ComplianceIssue(
                    category="Licensing",
                    message="Potential Editorial Content Detected.",
                    severity=Severity.INFO,
                    explanation=f"Keyword '{trigger}' suggests this might require an Editorial license instead of Commercial.",
                    actionable=False
                )
        return None