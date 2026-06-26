# ai/providers/openai_session.py
import logging
import httpx
from typing import Optional
from openai import OpenAI

from .openai_config import OpenAIConfig
from .openai_errors import OpenAIAuthenticationError

logger = logging.getLogger("OpenAISession")

class OpenAISession:
    """Controls the generation lifecycle, HTTP connection pools, and instances of the OpenAI SDK Client."""

    def __init__(self, config: OpenAIConfig):
        self.config = config
        self._client: Optional[OpenAI] = None
        self._http_client: Optional[httpx.Client] = None

    def initialize(self) -> None:
        """Instantiates the concrete HTTP clients and connects the OpenAI Client instance wrapper."""
        if not self.config.api_key:
            logger.error("OpenAI setup aborted: API Key configuration is missing.")
            raise OpenAIAuthenticationError("An API Key must be supplied to establish an OpenAI Session.")
            
        try:
            self._http_client = httpx.Client(
                timeout=httpx.Timeout(float(self.config.timeout_seconds)),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
            )
            self._client = OpenAI(
                api_key=self.config.api_key,
                http_client=self._http_client,
                max_retries=0
            )
            logger.info("OpenAI network subsystem and SDK clients initiated successfully.")
        except Exception as e:
            self.shutdown()
            logger.error(f"Failed to provision OpenAI clients: {str(e)}")
            raise

    def get_client(self) -> OpenAI:
        """Retrieves or creates the validated OpenAI client reference."""
        if self._client is None:
            self.initialize()
        return self._client

    def shutdown(self) -> None:
        """Safely tears down active HTTP connection pools and client sessions to prevent resource/socket leaks."""
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                logger.warning(f"Exception managed during OpenAI client cleanup: {str(e)}")
                
        if self._http_client:
            try:
                self._http_client.close()
            except Exception as e:
                logger.warning(f"Exception managed during HTTP transport cleanup: {str(e)}")
                
        self._client = None
        self._http_client = None
        logger.info("OpenAI background connection pools flushed and decommissioned.")