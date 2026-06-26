# metadata/title/title_validator.py
import logging
from dataclasses import dataclass, field
from typing import List

from metadata.title.title_rules import MarketplaceRules, DEFAULT_RULES

logger = logging.getLogger(__name__)

@dataclass
class ValidationReport:
    is_valid: bool
    title: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class TitleValidator:
    def __init__(self, rules: MarketplaceRules = DEFAULT_RULES):
        self.rules = rules

    def validate(self, title: str) -> ValidationReport:
        errors = []
        warnings = []
        
        if not title or title.isspace():
            errors.append("Title is empty.")
            return ValidationReport(is_valid=False, title=title, errors=errors)

        title_length = len(title)
        if title_length < self.rules.min_length:
            errors.append(f"Title is too short ({title_length} < {self.rules.min_length}).")
        if title_length > self.rules.max_length:
            errors.append(f"Title is too long ({title_length} > {self.rules.max_length}).")

        words = title.split()
        word_count = len(words)
        if word_count < self.rules.min_words:
            errors.append(f"Too few words ({word_count} < {self.rules.min_words}).")
        if word_count > self.rules.max_words:
            errors.append(f"Too many words ({word_count} > {self.rules.max_words}).")

        if self.rules.is_forbidden(title):
            errors.append("Contains forbidden keywords.")
            
        if self.rules.contains_trademark(title):
            errors.append("Contains trademarked or copyrighted names.")

        unique_words = set(w.lower() for w in words)
        if len(unique_words) < len(words) * 0.6:
            warnings.append("High word repetition detected.")

        if not title[0].isupper() and title[0].isalpha():
            warnings.append("Title should start with a capital letter.")

        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.debug(f"Validation failed for '{title}': {errors}")
            
        return ValidationReport(is_valid=is_valid, title=title, errors=errors, warnings=warnings)