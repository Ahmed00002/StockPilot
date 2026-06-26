# metadata/keywords/keyword_semantic.py
import difflib
from typing import List

class SemanticAnalyzer:
    def __init__(self, similarity_threshold: float = 0.85):
        self.threshold = similarity_threshold

    def calculate_similarity(self, word1: str, word2: str) -> float:
        return difflib.SequenceMatcher(None, word1.lower(), word2.lower()).ratio()

    def is_near_duplicate(self, word1: str, word2: str) -> bool:
        if word1.lower() == word2.lower():
            return True
            
        w1_parts = set(word1.lower().split())
        w2_parts = set(word2.lower().split())
        
        if w1_parts and w2_parts and w1_parts.issubset(w2_parts) or w2_parts.issubset(w1_parts):
            if len(w1_parts) == len(w2_parts):
                return True
                
        return self.calculate_similarity(word1, word2) >= self.threshold

DEFAULT_SEMANTIC_ANALYZER = SemanticAnalyzer()