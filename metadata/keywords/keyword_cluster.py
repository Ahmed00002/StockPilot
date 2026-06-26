# metadata/keywords/keyword_cluster.py
from typing import List, Dict, Set
from metadata.keywords.keyword_semantic import DEFAULT_SEMANTIC_ANALYZER
from metadata.keywords.keyword_synonyms import DEFAULT_SYNONYMS
from metadata.keywords.keyword_dictionary import DEFAULT_DICTIONARY

class KeywordClusterer:
    def __init__(self):
        self.semantic = DEFAULT_SEMANTIC_ANALYZER
        self.synonyms = DEFAULT_SYNONYMS
        self.dictionary = DEFAULT_DICTIONARY

    def cluster_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        clusters: Dict[str, List[str]] = {}
        processed: Set[str] = set()

        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in processed:
                continue

            base_concept = self.dictionary.to_singular(self.synonyms.get_base_concept(kw_lower))
            
            matched_cluster = None
            for root in clusters.keys():
                if self.semantic.is_near_duplicate(root, base_concept):
                    matched_cluster = root
                    break

            if matched_cluster:
                if kw not in clusters[matched_cluster]:
                    clusters[matched_cluster].append(kw)
            else:
                clusters[base_concept] = [kw]
                
            processed.add(kw_lower)

        return clusters

    def select_best_from_clusters(self, clusters: Dict[str, List[str]]) -> List[str]:
        selected = []
        for root, kws in clusters.items():
            kws.sort(key=lambda x: len(x.split()))
            selected.append(kws[0])
            if len(kws) > 2:
                selected.append(kws[1])
        return selected