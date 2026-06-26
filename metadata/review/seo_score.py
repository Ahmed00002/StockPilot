# metadata/review/seo_score.py
import logging
from typing import List, Set

from metadata.review.review_models import MetadataPackage

logger = logging.getLogger(__name__)

class SEOScoreCalculator:
    def __init__(self):
        self.ideal_title_length = 70
        self.ideal_desc_length = 150
        
    def calculate(self, package: MetadataPackage) -> float:
        score = 100.0
        
        title_len = len(package.title)
        if title_len < 30 or title_len > 100:
            score -= 10
            
        desc_len = len(package.description)
        if desc_len < 50 or desc_len > 300:
            score -= 10
            
        if len(package.keywords) < 20:
            score -= 20
        elif len(package.keywords) > 50:
            score -= 15
            
        title_words = set(package.title.lower().split())
        kw_set = set(k.lower() for k in package.keywords)
        
        overlap = len(title_words.intersection(kw_set))
        if overlap < 3 and len(title_words) > 3:
            score -= 15
            
        unique_kws = len(set(package.keywords))
        if unique_kws < len(package.keywords) * 0.9:
            score -= 15
            
        return max(0.0, min(100.0, score))