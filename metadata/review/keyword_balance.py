# metadata/review/keyword_balance.py
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class KeywordBalanceChecker:
    def __init__(self):
        self.action_suffixes = ("ing", "ion")
        self.concept_words = {"concept", "abstract", "background", "idea", "success"}

    def check(self, keywords: List[str]) -> List[Tuple[str, str]]:
        issues = []
        
        if len(keywords) < 5:
            return [("count_low", "Too few keywords. Minimum recommended is 15.")]
            
        action_count = sum(1 for k in keywords if any(k.lower().endswith(s) for s in self.action_suffixes))
        concept_count = sum(1 for k in keywords if k.lower() in self.concept_words)
        
        if action_count == 0:
            issues.append(("balance_action", "No action words detected. Consider adding verbs (-ing)."))
            
        long_tail = sum(1 for k in keywords if len(k.split()) > 1)
        if long_tail == 0:
            issues.append(("balance_longtail", "No multi-word phrases detected. Add specific long-tail keywords."))
            
        return issues