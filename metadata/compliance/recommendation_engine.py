# metadata/compliance/recommendation_engine.py
import logging
from typing import List
from metadata.compliance.compliance_models import ComplianceIssue

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        pass

    def filter_actionable(self, issues: List[ComplianceIssue]) -> List[ComplianceIssue]:
        return [issue for issue in issues if issue.actionable]