# metadata/description/description_validator.py
import logging
from dataclasses import dataclass, field
from typing import List

from metadata.description.description_rules import DescriptionRules, DEFAULT_DESCRIPTION_RULES

logger = logging.getLogger(__name__)

@dataclass
class ValidationReport:
    is_valid: bool
    description: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class DescriptionValidator:
    def __init__(self, rules: DescriptionRules = DEFAULT_DESCRIPTION_RULES):
        self.rules = rules

    def validate(self, description: str) -> ValidationReport:
        errors = []
        warnings = []
        
        if not description or description.isspace():
            errors.append("Description is empty.")
            return ValidationReport(is_valid=False, description=description, errors=errors)

        char_length = len(description)
        if char_length < self.rules.min_char_length:
            errors.append(f"Description too short in characters ({char_length} < {self.rules.min_char_length}).")
        if char_length > self.rules.max_char_length:
            errors.append(f"Description too long in characters ({char_length} > {self.rules.max_char_length}).")

        words = description.split()
        word_count = len(words)
        if word_count < self.rules.min_words:
            errors.append(f"Too few words ({word_count} < {self.rules.min_words}).")
        if word_count > self.rules.max_words:
            errors.append(f"Too many words ({word_count} > {self.rules.max_words}).")

        if self.rules.is_forbidden(description):
            errors.append("Contains forbidden or AI-generation keywords.")
            
        if self.rules.contains_trademark(description):
            errors.append("Contains trademarked or copyrighted entities.")

        sentences = description.split('.')
        if len(sentences) < 2 and word_count > 30:
            warnings.append("Run-on sentence detected; lacks proper punctuation.")

        unique_words = set(w.lower() for w in words)
        if len(unique_words) < len(words) * 0.4:
            warnings.append("Possible keyword stuffing detected; low vocabulary variance.")

        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.debug(f"Description validation failed: {errors}")
            
        return ValidationReport(is_valid=is_valid, description=description, errors=errors, warnings=warnings)