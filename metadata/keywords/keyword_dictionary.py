# metadata/keywords/keyword_dictionary.py
import re

class KeywordDictionary:
    def __init__(self):
        self.plural_rules = [
            (re.compile(r'ies$'), 'y'),
            (re.compile(r'es$'), ''),
            (re.compile(r's$'), '')
        ]

    def to_singular(self, word: str) -> str:
        word = word.lower()
        
        exceptions = {"business", "analysis", "glass", "canvas", "success"}
        if word in exceptions:
            return word

        for pattern, replacement in self.plural_rules:
            if pattern.search(word):
                candidate = pattern.sub(replacement, word)
                if len(candidate) > 2:
                    return candidate
        return word

    def is_plural_duplicate(self, word1: str, word2: str) -> bool:
        if word1 == word2:
            return True
        return self.to_singular(word1) == self.to_singular(word2)

DEFAULT_DICTIONARY = KeywordDictionary()