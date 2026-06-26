# metadata/review/grammar_checker.py
import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class GrammarChecker:
    def __init__(self):
        self.multiple_spaces = re.compile(r'\s{2,}')
        self.repeated_words = re.compile(r'\b(\w+)\s+\1\b', re.IGNORECASE)
        self.awkward_phrases = ["very unique", "completely full", "absolutely essential", "is showing"]

    def check(self, text: str) -> List[Tuple[str, str]]:
        issues = []
        
        if not text:
            return [("empty", "Text field is empty.")]

        if self.multiple_spaces.search(text):
            issues.append(("spacing", "Contains multiple consecutive spaces."))

        repeats = self.repeated_words.findall(text)
        if repeats:
            issues.append(("repetition", f"Contains repeated word: '{repeats[0]}'"))

        lower_text = text.lower()
        for phrase in self.awkward_phrases:
            if phrase in lower_text:
                issues.append(("awkward", f"Consider revising awkward phrase: '{phrase}'"))

        sentences = [s.strip() for s in text.split('.') if s.strip()]
        for sentence in sentences:
            if len(sentence.split()) < 3:
                issues.append(("incomplete", f"Potentially incomplete sentence: '{sentence}'"))
                
        return issues