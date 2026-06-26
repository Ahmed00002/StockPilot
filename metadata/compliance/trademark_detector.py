# metadata/compliance/trademark_detector.py
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class TrademarkDetector:
    def __init__(self):
        self.trademark_patterns = [
            re.compile(r'\bdisney\b', re.IGNORECASE),
            re.compile(r'\bmarvel\b', re.IGNORECASE),
            re.compile(r'\bstar\s?wars\b', re.IGNORECASE),
            re.compile(r'\blego\b', re.IGNORECASE),
            re.compile(r'\bporsche\b', re.IGNORECASE),
            re.compile(r'\bferrari\b', re.IGNORECASE),
            re.compile(r'\brolex\b', re.IGNORECASE),
            re.compile(r'\blouis\s?vuitton\b', re.IGNORECASE),
            re.compile(r'\bgucci\b', re.IGNORECASE),
            re.compile(r'\bharry\s?potter\b', re.IGNORECASE)
        ]

    def detect(self, text: str) -> List[Tuple[str, str]]:
        detected = []
        for pattern in self.trademark_patterns:
            match = pattern.search(text)
            if match:
                detected.append((match.group(0), "Protected trademark or franchise detected."))
        return detected