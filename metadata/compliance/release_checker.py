# metadata/compliance/release_checker.py
import logging
from typing import Optional, List
from metadata.compliance.compliance_models import ComplianceIssue, Severity

logger = logging.getLogger(__name__)

class ReleaseChecker:
    def __init__(self):
        self.person_triggers = {"man", "woman", "person", "people", "child", "girl", "boy", "face", "portrait", "crowd"}
        self.property_triggers = {"house", "building interior", "private property", "estate", "room"}

    def check(self, keywords: List[str]) -> List[ComplianceIssue]:
        issues = []
        lower_kws = set(k.lower() for k in keywords)
        
        if lower_kws.intersection(self.person_triggers):
            issues.append(ComplianceIssue(
                category="Legal",
                message="Model Release may be required.",
                severity=Severity.INFO,
                explanation="Keywords indicate people. Identifiable persons require a model release for commercial use.",
                actionable=False
            ))
            
        if lower_kws.intersection(self.property_triggers):
            issues.append(ComplianceIssue(
                category="Legal",
                message="Property Release may be required.",
                severity=Severity.INFO,
                explanation="Keywords indicate private property. Certain buildings or interiors require property releases.",
                actionable=False
            ))
            
        return issues