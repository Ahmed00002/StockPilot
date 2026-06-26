# metadata/compliance/brand_detector.py
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class BrandDetector:
    def __init__(self):
        self.brand_patterns = [
            re.compile(r'\bapple\b', re.IGNORECASE),
            re.compile(r'\bmicrosoft\b', re.IGNORECASE),
            re.compile(r'\bgoogle\b', re.IGNORECASE),
            re.compile(r'\bamazon\b', re.IGNORECASE),
            re.compile(r'\bfacebook\b', re.IGNORECASE),
            re.compile(r'\binstagram\b', re.IGNORECASE),
            re.compile(r'\bsamsung\b', re.IGNORECASE),
            re.compile(r'\bsony\b', re.IGNORECASE),
            re.compile(r'\bcoca\s?-?cola\b', re.IGNORECASE),
            re.compile(r'\bpepsi\b', re.IGNORECASE),
            re.compile(r'\bmcdonalds\b', re.IGNORECASE),
            re.compile(r'\bnike\b', re.IGNORECASE),
            re.compile(r'\badidas\b', re.IGNORECASE)
        ]

    def detect(self, text: str) -> List[Tuple[str, str]]:
        detected = []
        for pattern in self.brand_patterns:
            match = pattern.search(text)
            if match:
                detected.append((match.group(0), "Major corporate brand name detected."))
        return detected