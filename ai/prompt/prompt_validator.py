# ai/prompt/prompt_validator.py
from dataclasses import dataclass, field
from typing import List, Dict
import re

from .variable_resolver import VariableResolver

@dataclass
class ValidationReport:
    is_valid: bool
    missing_variables: List[str] = field(default_factory=list)
    empty_sections: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class PromptValidator:
    """Evaluates finalized prompt strings for logical completeness and syntactic integrity before dispatch."""

    @staticmethod
    def validate(final_prompt: str, original_template: str, provided_vars: Dict[str, str]) -> ValidationReport:
        report = ValidationReport(is_valid=True)
        
        # Check for un-resolved variables left over in the final prompt
        remaining_vars = VariableResolver.extract_variables(final_prompt)
        if remaining_vars:
            report.missing_variables = remaining_vars
            report.errors.append(f"Prompt contains unresolved variables: {', '.join(remaining_vars)}")
            report.is_valid = False

        # Validate structural boundaries
        if len(final_prompt.strip()) < 10:
            report.errors.append("Final generated prompt is suspiciously short (under 10 characters).")
            report.is_valid = False

        if "TODO" in final_prompt or "PLACEHOLDER" in final_prompt:
            report.warnings.append("Prompt contains developer placeholder text (TODO/PLACEHOLDER).")

        return report