# metadata/description/description_optimizer.py
import re
import logging

logger = logging.getLogger(__name__)

class DescriptionOptimizer:
    def __init__(self):
        self.multiple_spaces_regex = re.compile(r'\s+')
        self.punctuation_cleanup_regex = re.compile(r'\s+([,\.])')
        self.duplicate_punctuation_regex = re.compile(r'([,\.])\1+')

    def optimize(self, description: str) -> str:
        optimized = description.strip()
        optimized = self.multiple_spaces_regex.sub(' ', optimized)
        optimized = self.punctuation_cleanup_regex.sub(r'\1', optimized)
        optimized = self.duplicate_punctuation_regex.sub(r'\1', optimized)
        
        if not optimized:
            return ""

        sentences = re.split(r'(?<=[.!?])\s+', optimized)
        capitalized_sentences = []
        for sentence in sentences:
            if sentence and sentence[0].isalpha() and not sentence[0].isupper():
                sentence = sentence[0].upper() + sentence[1:]
            capitalized_sentences.append(sentence)
            
        optimized = ' '.join(capitalized_sentences)

        if not optimized.endswith(('.', '!', '?')):
            optimized += '.'

        logger.debug(f"Optimized description.")
        return optimized