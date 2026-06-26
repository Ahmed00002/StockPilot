# metadata/title/title_ranker.py
import logging
from dataclasses import dataclass
from typing import List
import re

logger = logging.getLogger(__name__)

@dataclass
class RankedTitle:
    title: str
    score: float
    seo_quality: float
    readability: float
    commercial_value: float

class TitleRanker:
    def __init__(self):
        self.ideal_length = 70 
        self.action_words = {"business", "corporate", "lifestyle", "technology", "modern", "background", "concept"}
        
    def rank(self, titles: List[str]) -> List[RankedTitle]:
        ranked_list = []
        for title in titles:
            seo_q = self._score_seo(title)
            read_q = self._score_readability(title)
            comm_q = self._score_commercial(title)
            
            overall = (seo_q * 0.4) + (comm_q * 0.4) + (read_q * 0.2)
            
            ranked_list.append(RankedTitle(
                title=title,
                score=round(overall, 2),
                seo_quality=round(seo_q, 2),
                readability=round(read_q, 2),
                commercial_value=round(comm_q, 2)
            ))
            
        ranked_list.sort(key=lambda x: x.score, reverse=True)
        return ranked_list

    def _score_seo(self, title: str) -> float:
        score = 100.0
        length = len(title)
        length_penalty = abs(self.ideal_length - length) * 0.5
        score -= length_penalty
        
        words = title.lower().split()
        unique_ratio = len(set(words)) / max(len(words), 1)
        if unique_ratio < 0.8:
            score -= (1.0 - unique_ratio) * 50
            
        return max(0.0, min(100.0, score))

    def _score_readability(self, title: str) -> float:
        score = 100.0
        if len(title.split()) > 15:
            score -= 20
        if re.search(r'\d{3,}', title):
            score -= 10
        if title.count(',') > 3:
            score -= 15
        return max(0.0, min(100.0, score))

    def _score_commercial(self, title: str) -> float:
        score = 50.0 
        words = set(title.lower().split())
        hits = len(words.intersection(self.action_words))
        score += hits * 10
        if "abstract" in words or "concept" in words:
            score += 5
        return max(0.0, min(100.0, score))