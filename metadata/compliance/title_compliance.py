# metadata/compliance/title_compliance.py
import logging
from typing import List, Any
from metadata.compliance.compliance_models import ComplianceIssue, Severity
from metadata.compliance.restricted_terms import DEFAULT_RESTRICTED_TERMS

logger = logging.getLogger(__name__)

class TitleComplianceValidator:
    def __init__(self):
        self.restricted = DEFAULT_RESTRICTED_TERMS

    def validate(self, title: str, rules: Any) -> List[ComplianceIssue]:
        issues = []
        
        if not title:
            issues.append(ComplianceIssue("Title", "Title is empty.", Severity.CRITICAL, "A title is required for upload.", True))
            return issues

        length = len(title)
        if length < rules.min_title_length:
            issues.append(ComplianceIssue("Title", "Title is too short.", Severity.CRITICAL, f"Minimum length is {rules.min_title_length} characters.", True))
        elif length > rules.max_title_length:
            issues.append(ComplianceIssue("Title", "Title is too long.", Severity.CRITICAL, f"Maximum length is {rules.max_title_length} characters.", True))

        if self.restricted.contains_restricted(title):
            issues.append(ComplianceIssue("Title", "Contains restricted AI-generation terms.", Severity.CRITICAL, "Marketplaces prohibit AI prompt terms in metadata.", True))

        if self.restricted.contains_spam(title):
            issues.append(ComplianceIssue("Title", "Contains spam or promotional phrasing.", Severity.WARNING, "Promotional phrases reduce search visibility.", True))

        if title[0].isalpha() and not title[0].isupper():
            issues.append(ComplianceIssue("Title", "Does not start with a capital letter.", Severity.INFO, "Capitalization improves professionalism.", True))

        return issues