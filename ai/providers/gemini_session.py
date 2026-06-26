# ai/providers/gemini_session.py
import logging
import google.generativeai as genai
from typing import Optional

from .gemini_config import GeminiConfig
from .gemini_errors import GeminiAuthenticationError

logger = logging.getLogger("GeminiSession")

class GeminiSession:
    """Manages the lifecycle and configuration of the Google Generative AI client."""

    def __init__(self, config: GeminiConfig):
        self.config = config
        self._is_configured = False

    def initialize(self) -> None:
        """Configures the underlying SDK with the provided API key."""
        if not self.config.api_key:
            logger.error("Attempted to initialize Gemini session without an API key.")
            raise GeminiAuthenticationError("API key is required for Gemini initialization.")
            
        try:
            genai.configure(api_key=self.config.api_key)
            self._is_configured = True
            logger.info("Gemini SDK configured successfully.")
        except Exception as e:
            self._is_configured = False
            logger.error(f"Failed to configure Gemini SDK: {str(e)}")
            raise

    def get_model(self, model_name: str) -> Optional[genai.GenerativeModel]:
        """
        Instantiates a GenerativeModel object for the specified model.
        
        Args:
            model_name: The name of the Gemini model to load.
            
        Returns:
            GenerativeModel: The instantiated model.
        """
        if not self._is_configured:
            self.initialize()
            
        try:
            return genai.GenerativeModel(model_name=model_name)
        except Exception as e:
            logger.error(f"Failed to load Gemini model '{model_name}': {str(e)}")
            raise

    def shutdown(self) -> None:
        """Cleans up session configuration."""
        self._is_configured = False
        # The genai SDK doesn't have an explicit close/shutdown for configure(),
        # so we clear the internal state indicator.
        logger.info("Gemini session shutdown complete.")