# metadata/compliance/warning_engine.py
import logging
from typing import List
from metadata.compliance.compliance_models import ComplianceIssue, Severity

logger = logging.getLogger(__name__)

class WarningEngine:
    def __init__(self):
        pass

    def filter_warnings(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        return [issue for issue in issues if issue.severity in (Severity.WARNING, Severity.CRITICAL)]