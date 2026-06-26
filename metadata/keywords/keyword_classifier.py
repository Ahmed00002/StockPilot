# metadata/keywords/keyword_classifier.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set

class KeywordCategory(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACTION = "action"
    EMOTION = "emotion"
    CONCEPT = "concept"
    INDUSTRY = "industry"
    LOCATION = "location"
    COLOR = "color"
    LONG_TAIL = "long_tail"
    UNKNOWN = "unknown"

@dataclass
class ClassifiedKeyword:
    word: str
    category: KeywordCategory
    buyer_intent: List[str]

class KeywordClassifier:
    def __init__(self):
        self.action_suffixes = {"ing", "ion"}
        self.color_words = {"red", "blue", "green", "yellow", "black", "white", "orange", "purple", "pink"}
        self.emotion_words = {"happy", "sad", "angry", "joy", "depression", "success", "stress", "love"}
        
    def classify(self, keyword: str, primary_subjects: Set[str]) -> ClassifiedKeyword:
        lower_kw = keyword.lower()
        words = lower_kw.split()
        
        category = KeywordCategory.UNKNOWN
        
        if lower_kw in primary_subjects:
            category = KeywordCategory.PRIMARY
        elif len(words) >= 3:
            category = KeywordCategory.LONG_TAIL
        elif lower_kw in self.color_words:
            category = KeywordCategory.COLOR
        elif lower_kw in self.emotion_words:
            category = KeywordCategory.EMOTION
        elif any(w.endswith(suffix) for w in words for suffix in self.action_suffixes):
            category = KeywordCategory.ACTION
        else:
            category = KeywordCategory.SECONDARY
            
        intents = self._estimate_buyer_intent(lower_kw)
        
        return ClassifiedKeyword(word=keyword, category=category, buyer_intent=intents)

    def _estimate_buyer_intent(self, keyword: str) -> List[str]:
        intents = []
        if "business" in keyword or "office" in keyword:
            intents.append("corporate")
        if "health" in keyword or "medical" in keyword:
            intents.append("healthcare")
        if "school" in keyword or "learn" in keyword:
            intents.append("education")
        if not intents:
            intents.append("general")
        return intents