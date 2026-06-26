# metadata/description/description_ranker.py
import logging
import re
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class RankedDescription:
    description: str
    score: float
    seo_quality: float
    readability: float
    commercial_value: float

class DescriptionRanker:
    def __init__(self):
        self.ideal_word_length = 40
        self.commercial_markers = {"perfect for", "ideal for", "background", "concept", "business", "design", "template", "suitable", "industry", "lifestyle", "commercial"}
        
    def rank(self, descriptions: List[str]) -> List[RankedDescription]:
        ranked_list = []
        for desc in descriptions:
            seo_q = self._score_seo(desc)
            read_q = self._score_readability(desc)
            comm_q = self._score_commercial(desc)
            
            overall = (seo_q * 0.35) + (comm_q * 0.35) + (read_q * 0.30)
            
            ranked_list.append(RankedDescription(
                description=desc,
                score=round(overall, 2),
                seo_quality=round(seo_q, 2),
                readability=round(read_q, 2),
                commercial_value=round(comm_q, 2)
            ))
            
        ranked_list.sort(key=lambda x: x.score, reverse=True)
        return ranked_list

    def _score_seo(self, desc: str) -> float:
        score = 100.0
        words = desc.lower().split()
        length = len(words)
        
        length_penalty = abs(self.ideal_word_length - length) * 1.5
        score -= min(40, length_penalty)
        
        unique_ratio = len(set(words)) / max(len(words), 1)
        if unique_ratio < 0.6:
            score -= (0.6 - unique_ratio) * 100
            
        return max(0.0, min(100.0, score))

    def _score_readability(self, desc: str) -> float:
        score = 100.0
        sentences = [s for s in re.split(r'[.!?]', desc) if s.strip()]
        
        if not sentences:
            return 0.0
            
        avg_words_per_sentence = len(desc.split()) / len(sentences)
        if avg_words_per_sentence > 25:
            score -= (avg_words_per_sentence - 25) * 2
        elif avg_words_per_sentence < 5:
            score -= 20
            
        return max(0.0, min(100.0, score))

    def _score_commercial(self, desc: str) -> float:
        score = 40.0 
        words = set(desc.lower().split())
        hits = len(words.intersection(self.commercial_markers))
        score += hits * 15
        
        if "vector" in desc.lower() or "illustration" in desc.lower():
            score += 10
            
        return max(0.0, min(100.0, score))