# metadata/description/description_rules.py
import re
from dataclasses import dataclass, field
from typing import List, Pattern

@dataclass
class DescriptionRules:
    min_char_length: int = 20
    max_char_length: int = 500
    min_words: int = 5
    max_words: int = 100
    forbidden_words: List[str] = field(default_factory=lambda: [
        "ai generated", "midjourney", "dall-e", "stable diffusion", 
        "generative ai", "prompt", "artificial intelligence generated"
    ])
    trademark_patterns: List[Pattern] = field(default_factory=lambda: [
        re.compile(r'\bapple\b', re.IGNORECASE),
        re.compile(r'\bmicrosoft\b', re.IGNORECASE),
        re.compile(r'\bnike\b', re.IGNORECASE),
        re.compile(r'\bdisney\b', re.IGNORECASE),
        re.compile(r'\bmarvel\b', re.IGNORECASE),
        re.compile(r'\bcoca-?cola\b', re.IGNORECASE),
        re.compile(r'\bgoogle\b', re.IGNORECASE)
    ])

    def is_forbidden(self, text: str) -> bool:
        lower_text = text.lower()
        return any(word in lower_text for word in self.forbidden_words)

    def contains_trademark(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.trademark_patterns)

DEFAULT_DESCRIPTION_RULES = DescriptionRules()