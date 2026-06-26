# metadata/review/confidence_score.py
import logging
from typing import List

logger = logging.getLogger(__name__)

class ConfidenceScoreCalculator:
    def __init__(self):
        pass

    def calculate(self, original_confidence: float, validation_issues: int) -> float:
        score = original_confidence * 100.0
        penalty = min(validation_issues * 5.0, 40.0)
        score -= penalty
        return max(0.0, min(100.0, score))