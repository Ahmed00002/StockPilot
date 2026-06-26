# metadata/review/trademark_checker.py
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class TrademarkChecker:
    def __init__(self):
        self.trademarks = [
            re.compile(r'\bapple\b', re.IGNORECASE),
            re.compile(r'\bmicrosoft\b', re.IGNORECASE),
            re.compile(r'\bnike\b', re.IGNORECASE),
            re.compile(r'\bdisney\b', re.IGNORECASE),
            re.compile(r'\bmarvel\b', re.IGNORECASE),
            re.compile(r'\bcoca\s?-?cola\b', re.IGNORECASE),
            re.compile(r'\bgoogle\b', re.IGNORECASE),
            re.compile(r'\bfacebook\b', re.IGNORECASE),
            re.compile(r'\binstagram\b', re.IGNORECASE),
            re.compile(r'\btwitter\b', re.IGNORECASE),
            re.compile(r'\bporsche\b', re.IGNORECASE)
        ]

    def check(self, text: str) -> List[Tuple[str, str]]:
        issues = []
        for pattern in self.trademarks:
            match = pattern.search(text)
            if match:
                issues.append(("trademark", f"Potential trademark detected: '{match.group(0)}'"))
        return issues