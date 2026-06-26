# metadata/review/commercial_score.py
import logging
from typing import List, Set

from metadata.review.review_models import MetadataPackage

logger = logging.getLogger(__name__)

class CommercialScoreCalculator:
    def __init__(self):
        self.commercial_terms = {
            "business", "corporate", "professional", "office", "design", "background", 
            "template", "marketing", "industry", "lifestyle", "modern", "concept",
            "technology", "communication", "success"
        }
        
    def calculate(self, package: MetadataPackage) -> float:
        score = 50.0 
        
        all_text = f"{package.title} {package.description} {' '.join(package.keywords)}".lower()
        words = set(all_text.split())
        
        hits = len(words.intersection(self.commercial_terms))
        score += min(40.0, hits * 8.0)
        
        if len(package.title.split()) >= 5:
            score += 5.0
            
        if len(package.description.split('.')) >= 2:
            score += 5.0
            
        return max(0.0, min(100.0, score))