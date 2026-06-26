# metadata/review/review_validator.py
import logging
from typing import List

from metadata.review.review_models import MetadataPackage, ReviewRecommendation, ReviewSeverity
from metadata.review.grammar_checker import GrammarChecker
from metadata.review.trademark_checker import TrademarkChecker
from metadata.review.duplicate_checker import DuplicateChecker
from metadata.review.metadata_consistency import ConsistencyChecker
from metadata.review.keyword_balance import KeywordBalanceChecker

logger = logging.getLogger(__name__)

class ReviewValidator:
    def __init__(self):
        self.grammar = GrammarChecker()
        self.trademark = TrademarkChecker()
        self.duplicate = DuplicateChecker()
        self.consistency = ConsistencyChecker()
        self.kw_balance = KeywordBalanceChecker()

    def run_validation(self, package: MetadataPackage) -> List[ReviewRecommendation]:
        recs = []
        
        for field_name, text in [("Title", package.title), ("Description", package.description)]:
            issues = self.grammar.check(text)
            for issue_type, msg in issues:
                recs.append(ReviewRecommendation(category="Grammar", message=f"[{field_name}] {msg}", severity=ReviewSeverity.WARNING, explanation="Improves readability and professionalism.", actionable=True))

        for field_name, text in [("Title", package.title), ("Description", package.description)]:
            issues = self.trademark.check(text)
            for issue_type, msg in issues:
                recs.append(ReviewRecommendation(category="Compliance", message=f"[{field_name}] {msg}", severity=ReviewSeverity.CRITICAL, explanation="Trademarks can cause marketplace rejection.", actionable=True))
                
        for kw in package.keywords:
            issues = self.trademark.check(kw)
            for issue_type, msg in issues:
                recs.append(ReviewRecommendation(category="Compliance", message=f"[Keyword] {msg}", severity=ReviewSeverity.CRITICAL, explanation="Trademarks can cause marketplace rejection.", actionable=True))

        dup_kw_issues = self.duplicate.check_keywords(package.keywords)
        for issue_type, msg in dup_kw_issues:
            recs.append(ReviewRecommendation(category="Quality", message=msg, severity=ReviewSeverity.WARNING, explanation="Duplicate keywords waste slots.", actionable=True))

        cons_issues = self.consistency.check(package)
        for issue_type, msg in cons_issues:
            recs.append(ReviewRecommendation(category="Consistency", message=msg, severity=ReviewSeverity.INFO, explanation="Improves search relevance.", actionable=True))

        bal_issues = self.kw_balance.check(package.keywords)
        for issue_type, msg in bal_issues:
            recs.append(ReviewRecommendation(category="SEO", message=msg, severity=ReviewSeverity.INFO, explanation="Improves discovery across different intents.", actionable=True))

        return recs