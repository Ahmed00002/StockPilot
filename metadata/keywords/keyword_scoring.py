# metadata/keywords/keyword_scoring.py
from dataclasses import dataclass

@dataclass
class KeywordScore:
    seo_score: float
    commercial_score: float
    relevance_score: float
    confidence_score: float
    
    @property
    def overall(self) -> float:
        return (
            (self.seo_score * 0.3) + 
            (self.commercial_score * 0.3) + 
            (self.relevance_score * 0.25) + 
            (self.confidence_score * 0.15)
        )

class KeywordScoringEngine:
    def __init__(self):
        self.commercial_markers = {"business", "corporate", "office", "design", "background", "technology", "modern", "lifestyle", "concept"}
        
    def calculate_score(self, keyword: str, is_primary: bool, confidence: float) -> KeywordScore:
        kw_lower = keyword.lower()
        words = kw_lower.split()
        
        seo = 100.0 if len(words) <= 2 else max(50.0, 100.0 - (len(words) - 2) * 15.0)
        
        comm = 50.0
        if any(marker in words for marker in self.commercial_markers):
            comm += 30.0
        if len(words) > 1:
            comm += 10.0 
            
        relevance = 100.0 if is_primary else 60.0
        
        return KeywordScore(
            seo_score=min(100.0, seo),
            commercial_score=min(100.0, comm),
            relevance_score=relevance,
            confidence_score=confidence * 100.0
        )