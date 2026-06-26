# metadata/keywords/keyword_confidence.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class VisionConfidence:
    subject_confidence: float = 1.0
    scene_confidence: float = 1.0
    object_confidence: float = 1.0

class KeywordConfidenceTracker:
    def __init__(self):
        self.keyword_confidence: Dict[str, float] = {}

    def register_confidence(self, keyword: str, confidence: float):
        current = self.keyword_confidence.get(keyword.lower(), 0.0)
        self.keyword_confidence[keyword.lower()] = max(current, confidence)

    def get_confidence(self, keyword: str) -> float:
        return self.keyword_confidence.get(keyword.lower(), 0.5)