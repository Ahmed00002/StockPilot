# metadata/review/readability_score.py
import re
import logging

logger = logging.getLogger(__name__)

class ReadabilityCalculator:
    def __init__(self):
        pass

    def calculate(self, text: str) -> float:
        if not text or len(text.strip()) == 0:
            return 0.0
            
        score = 100.0
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return 0.0
            
        words = text.split()
        avg_sentence_length = len(words) / len(sentences)
        
        if avg_sentence_length > 25:
            score -= (avg_sentence_length - 25) * 2.0
        elif avg_sentence_length < 5:
            score -= 15.0
            
        long_words = sum(1 for w in words if len(w) > 10)
        long_word_ratio = long_words / max(len(words), 1)
        
        if long_word_ratio > 0.3:
            score -= 20.0
            
        return max(0.0, min(100.0, score))