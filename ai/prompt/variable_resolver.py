# ai/prompt/variable_resolver.py
import re
import logging
from typing import Dict, List

logger = logging.getLogger("VariableResolver")

class VariableResolver:
    """Scans and injects dynamic dictionary boundaries directly into prompt string targets."""

    PLACEHOLDER_PATTERN = re.compile(r"\{\{(.*?)\}\}")

    @staticmethod
    def resolve(content: str, variables: Dict[str, str]) -> str:
        """
        Replaces all {{variable_name}} occurrences in the content string.
        """
        resolved_content = content

        def replacer(match):
            var_name = match.group(1).strip()
            # If variable is known, insert it. Otherwise, leave the placeholder intact.
            if var_name in variables:
                val = variables[var_name]
                return str(val) if val is not None else ""
            else:
                logger.warning(f"Unresolved prompt variable encountered during execution: {var_name}")
                return match.group(0)

        resolved_content = VariableResolver.PLACEHOLDER_PATTERN.sub(replacer, resolved_content)
        return resolved_content

    @staticmethod
    def extract_variables(content: str) -> List[str]:
        """Parses a raw prompt template to identify all expected placeholder requirements."""
        matches = VariableResolver.PLACEHOLDER_PATTERN.findall(content)
        return list(set(match.strip() for match in matches))