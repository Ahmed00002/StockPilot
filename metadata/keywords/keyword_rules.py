# metadata/keywords/keyword_rules.py
import re
from dataclasses import dataclass, field
from typing import List, Pattern

@dataclass
class KeywordRules:
    min_keywords: int = 5
    max_keywords: int = 50
    ideal_keywords: int = 40
    min_keyword_length: int = 3
    max_keyword_length: int = 50
    max_words_per_phrase: int = 4
    
    trademark_patterns: List[Pattern] = field(default_factory=lambda: [
        re.compile(r'\bapple\b', re.IGNORECASE),
        re.compile(r'\bmicrosoft\b', re.IGNORECASE),
        re.compile(r'\bnike\b', re.IGNORECASE),
        re.compile(r'\bdisney\b', re.IGNORECASE),
        re.compile(r'\bporsche\b', re.IGNORECASE),
        re.compile(r'\bcoca\s?-?cola\b', re.IGNORECASE)
    ])
    
    def is_valid_length(self, count: int) -> bool:
        return self.min_keywords <= count <= self.max_keywords

    def contains_trademark(self, keyword: str) -> bool:
        return any(pattern.search(keyword) for pattern in self.trademark_patterns)

DEFAULT_KEYWORD_RULES = KeywordRules()