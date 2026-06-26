# metadata/compliance/keyword_compliance.py
import collections
import logging
from typing import List, Any
from metadata.compliance.compliance_models import ComplianceIssue, Severity
from metadata.compliance.restricted_terms import DEFAULT_RESTRICTED_TERMS

logger = logging.getLogger(__name__)

class KeywordComplianceValidator:
    def __init__(self):
        self.restricted = DEFAULT_RESTRICTED_TERMS

    def validate(self, keywords: List[str], rules: Any) -> List[ComplianceIssue]:
        issues = []
        count = len(keywords)
        
        if count < rules.min_keywords:
            issues.append(ComplianceIssue("Keywords", "Too few keywords.", Severity.CRITICAL, f"Minimum required is {rules.min_keywords}.", True))
        elif count > rules.max_keywords:
            issues.append(ComplianceIssue("Keywords", "Too many keywords.", Severity.CRITICAL, f"Maximum allowed is {rules.max_keywords}.", True))

        lower_kws = [k.lower() for k in keywords]
        duplicates = [item for item, count in collections.Counter(lower_kws).items() if count > 1]
        if duplicates:
            issues.append(ComplianceIssue("Keywords", "Duplicate keywords detected.", Severity.WARNING, "Duplicates waste keyword slots and may cause rejection.", True))

        for kw in keywords:
            if self.restricted.contains_restricted(kw):
                issues.append(ComplianceIssue("Keywords", f"Restricted term found: '{kw}'", Severity.CRITICAL, "AI generation terms are prohibited.", True))
            elif self.restricted.contains_spam(kw):
                 issues.append(ComplianceIssue("Keywords", f"Spam term found: '{kw}'", Severity.WARNING, "Promotional terms are not allowed.", True))

        return issues