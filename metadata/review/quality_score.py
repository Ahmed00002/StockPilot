# metadata/review/quality_score.py
import logging
from metadata.review.review_models import ComponentScores

logger = logging.getLogger(__name__)

class QualityScoreCalculator:
    def __init__(self):
        self.weights = {
            "seo": 0.25,
            "commercial": 0.25,
            "grammar": 0.15,
            "marketplace": 0.15,
            "readability": 0.10,
            "confidence": 0.10
        }

    def calculate_overall(self, scores: ComponentScores) -> float:
        overall = (
            (scores.seo * self.weights["seo"]) +
            (scores.commercial * self.weights["commercial"]) +
            (scores.grammar * self.weights["grammar"]) +
            (scores.marketplace * self.weights["marketplace"]) +
            (scores.readability * self.weights["readability"]) +
            (scores.confidence * self.weights["confidence"])
        )
        return round(overall, 2)

    def calculate_component_score(self, base_score: float, penalties: int, penalty_weight: float = 5.0) -> float:
        score = base_score - (penalties * penalty_weight)
        return max(0.0, min(100.0, score))