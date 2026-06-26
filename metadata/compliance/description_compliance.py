# metadata/compliance/description_compliance.py
import logging
import re
from typing import List, Any
from metadata.compliance.compliance_models import ComplianceIssue, Severity
from metadata.compliance.restricted_terms import DEFAULT_RESTRICTED_TERMS

logger = logging.getLogger(__name__)

class DescriptionComplianceValidator:
    def __init__(self):
        self.restricted = DEFAULT_RESTRICTED_TERMS

    def validate(self, description: str, rules: Any) -> List[ComplianceIssue]:
        issues = []
        
        if not description:
            issues.append(ComplianceIssue("Description", "Description is empty.", Severity.WARNING, "A description is highly recommended.", True))
            return issues

        length = len(description)
        if length > rules.max_desc_length:
            issues.append(ComplianceIssue("Description", "Description is too long.", Severity.WARNING, f"Maximum recommended length is {rules.max_desc_length} characters.", True))

        if self.restricted.contains_restricted(description):
            issues.append(ComplianceIssue("Description", "Contains restricted AI-generation terms.", Severity.CRITICAL, "Marketplaces prohibit AI prompt terms in metadata.", True))

        if self.restricted.contains_spam(description):
            issues.append(ComplianceIssue("Description", "Contains spam or promotional phrasing.", Severity.WARNING, "Promotional phrases reduce search visibility.", True))

        sentences = [s.strip() for s in re.split(r'[.!?]+', description) if s.strip()]
        if len(sentences) < 1:
             issues.append(ComplianceIssue("Description", "Description lacks punctuation.", Severity.INFO, "Use proper sentences for readability.", True))

        return issues