# ai/prompt/language_rules.py
import logging
from typing import Dict

logger = logging.getLogger("LanguageRules")

class LanguageRulesEngine:
    """Manages linguistic formatting rules, encoding expectations, and output translation directives."""

    _LANGUAGE_DIRECTIVES: Dict[str, str] = {
        "English": "Generate all content strictly in American English. Ensure natural phrasing and correct spelling.",
        "Spanish": "Generate all content strictly in Spanish. Maintain professional tone.",
        "French": "Generate all content strictly in French. Maintain professional tone.",
        "German": "Generate all content strictly in German. Maintain professional tone.",
        "Japanese": "Generate all content strictly in Japanese. Use formal phrasing suitable for stock metadata."
    }

    @staticmethod
    def get_directive(language: str) -> str:
        """Retrieves system prompting instructions for enforcing specific language outputs."""
        if not language:
            return LanguageRulesEngine._LANGUAGE_DIRECTIVES["English"]
            
        directive = LanguageRulesEngine._LANGUAGE_DIRECTIVES.get(language)
        if not directive:
            logger.warning(f"Unsupported language requested: {language}. Falling back to English directive structure.")
            return LanguageRulesEngine._LANGUAGE_DIRECTIVES["English"]
            
        return directive