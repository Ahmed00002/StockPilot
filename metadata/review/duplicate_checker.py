# metadata/review/duplicate_checker.py
import collections
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class DuplicateChecker:
    def __init__(self):
        pass

    def check_keywords(self, keywords: List[str]) -> List[Tuple[str, str]]:
        issues = []
        lower_keywords = [k.lower() for k in keywords]
        counts = collections.Counter(lower_keywords)
        
        for kw, count in counts.items():
            if count > 1:
                issues.append(("duplicate_keyword", f"Keyword '{kw}' appears {count} times."))
                
        return issues

    def check_text(self, text: str) -> List[Tuple[str, str]]:
        issues = []
        sentences = [s.strip().lower() for s in text.split('.') if s.strip()]
        counts = collections.Counter(sentences)
        
        for sentence, count in counts.items():
            if count > 1:
                issues.append(("duplicate_sentence", f"Sentence appears {count} times: '{sentence[:30]}...'"))
                
        return issues