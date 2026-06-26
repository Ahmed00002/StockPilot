# metadata/title/title_optimizer.py
import re
import logging

logger = logging.getLogger(__name__)

class TitleOptimizer:
    def __init__(self):
        self.multiple_spaces_regex = re.compile(r'\s+')
        self.punctuation_cleanup_regex = re.compile(r'[^\w\s\-\,\.]')

    def optimize(self, title: str) -> str:
        optimized = title.strip()
        optimized = self.multiple_spaces_regex.sub(' ', optimized)
        optimized = self.punctuation_cleanup_regex.sub('', optimized)
        
        if not optimized:
            return ""

        optimized = optimized.replace(" ,", ",").replace(" .", ".")
        
        if optimized[0].isalpha() and not optimized[0].isupper():
            optimized = optimized[0].upper() + optimized[1:]

        if optimized.endswith('.'):
            optimized = optimized[:-1]

        logger.debug(f"Optimized title from '{title}' to '{optimized}'")
        return optimized