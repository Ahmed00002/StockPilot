# metadata/keywords/keyword_synonyms.py
from typing import Dict, Set

class KeywordSynonyms:
    def __init__(self):
        self._synonym_groups: Dict[str, str] = {
            "workplace": "office",
            "workspace": "office",
            "computer": "pc",
            "laptop": "notebook",
            "cellphone": "smartphone",
            "mobile phone": "smartphone",
            "automobile": "car",
            "vehicle": "car",
            "photograph": "photo",
            "picture": "image",
            "joy": "happiness",
            "glad": "happy",
            "sadness": "depression"
        }

    def get_base_concept(self, keyword: str) -> str:
        return self._synonym_groups.get(keyword.lower(), keyword.lower())

    def are_synonyms(self, kw1: str, kw2: str) -> bool:
        return self.get_base_concept(kw1) == self.get_base_concept(kw2)

DEFAULT_SYNONYMS = KeywordSynonyms()