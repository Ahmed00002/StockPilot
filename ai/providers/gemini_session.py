# ai/providers/gemini_session.py
import logging
from typing import Optional

from .gemini_config import GeminiConfig
from .gemini_errors import GeminiAuthenticationError

logger = logging.getLogger("GeminiSession")


def _import_genai():
    """Lazily import google-generativeai so the app starts even without it."""
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        raise ImportError(
            "The 'google-generativeai' package is not installed.\n"
            "Install it with:  pip install google-generativeai"
        )


class GeminiSession:
    """Manages the lifecycle and configuration of the Google Generative AI client."""

    def __init__(self, config: GeminiConfig):
        self.config = config
        self._is_configured = False

    def initialize(self) -> None:
        if not self.config.api_key:
            logger.error("Attempted to initialize Gemini session without an API key.")
            raise GeminiAuthenticationError("API key is required for Gemini initialization.")

        genai = _import_genai()
        try:
            genai.configure(api_key=self.config.api_key)
            self._is_configured = True
            logger.info("Gemini SDK configured successfully.")
        except Exception as e:
            self._is_configured = False
            logger.error(f"Failed to configure Gemini SDK: {str(e)}")
            raise

    def get_model(self, model_name: str):
        genai = _import_genai()
        if not self._is_configured:
            self.initialize()
        try:
            return genai.GenerativeModel(model_name=model_name)
        except Exception as e:
            logger.error(f"Failed to load Gemini model '{model_name}': {str(e)}")
            raise

    def shutdown(self) -> None:
        self._is_configured = False
        logger.info("Gemini session shutdown complete.")
