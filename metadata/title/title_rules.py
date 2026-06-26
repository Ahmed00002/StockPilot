# metadata/title/title_rules.py
import re
from dataclasses import dataclass, field
from typing import List, Pattern

@dataclass
class MarketplaceRules:
    min_length: int = 5
    max_length: int = 200
    max_words: int = 50
    min_words: int = 3
    forbidden_words: List[str] = field(default_factory=lambda: [
        "vector", "illustration", "seamless", "pattern", "ai generated", 
        "midjourney", "dalle", "stable diffusion", "3d render", "generative ai"
    ])
    trademark_patterns: List[Pattern] = field(default_factory=lambda: [
        re.compile(r'\bapple\b', re.IGNORECASE),
        re.compile(r'\bmicrosoft\b', re.IGNORECASE),
        re.compile(r'\bnike\b', re.IGNORECASE),
        re.compile(r'\bdisney\b', re.IGNORECASE),
        re.compile(r'\bmarvel\b', re.IGNORECASE),
        re.compile(r'\bporsche\b', re.IGNORECASE),
        re.compile(r'\bferrari\b', re.IGNORECASE)
    ])
    required_patterns: List[Pattern] = field(default_factory=list)

    def is_forbidden(self, text: str) -> bool:
        lower_text = text.lower()
        return any(word in lower_text for word in self.forbidden_words)

    def contains_trademark(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.trademark_patterns)

DEFAULT_RULES = MarketplaceRules()