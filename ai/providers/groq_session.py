# ai/providers/groq_session.py
import logging
import httpx
from typing import Optional

from .groq_config import GroqConfig
from .groq_errors import GroqAuthenticationError

logger = logging.getLogger("GroqSession")


def _import_groq():
    """Lazily import the groq SDK so the app starts even without it installed."""
    try:
        from groq import Groq
        return Groq
    except ImportError:
        raise ImportError(
            "The 'groq' package is not installed.\n"
            "Install it with:  pip install groq"
        )


class GroqSession:
    """Controls the generation lifecycle, HTTP connection pools, and instances of the Groq Client."""

    def __init__(self, config: GroqConfig):
        self.config = config
        self._client = None
        self._http_client: Optional[httpx.Client] = None

    def initialize(self) -> None:
        if not self.config.api_key:
            logger.error("Groq setup aborted: API Key configuration is missing.")
            raise GroqAuthenticationError("An API Key must be supplied to establish a Groq Session.")

        Groq = _import_groq()
        try:
            self._http_client = httpx.Client(
                timeout=httpx.Timeout(float(self.config.timeout_seconds)),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
            )
            self._client = Groq(
                api_key=self.config.api_key,
                http_client=self._http_client,
                max_retries=0
            )
            logger.info("Groq network subsystem and SDK clients initiated successfully.")
        except Exception as e:
            self.shutdown()
            logger.error(f"Failed to provision Groq clients: {str(e)}")
            raise

    def get_client(self):
        if self._client is None:
            self.initialize()
        return self._client

    def shutdown(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                logger.warning(f"Exception managed during Groq client cleanup: {str(e)}")

        if self._http_client:
            try:
                self._http_client.close()
            except Exception as e:
                logger.warning(f"Exception managed during HTTP transport cleanup: {str(e)}")

        self._client = None
        self._http_client = None
        logger.info("Groq background connection pools flushed and decommissioned.")
