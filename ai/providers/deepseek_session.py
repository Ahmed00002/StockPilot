# ai/providers/deepseek_session.py
import logging
import httpx
from typing import Optional

from .deepseek_config import DeepSeekConfig
from .deepseek_errors import DeepSeekAuthenticationError

logger = logging.getLogger("DeepSeekSession")


def _import_openai():
    """Lazily import the openai SDK (used for DeepSeek compatibility)."""
    try:
        from openai import OpenAI
        return OpenAI
    except ImportError:
        raise ImportError(
            "The 'openai' package is not installed.\n"
            "Install it with:  pip install openai"
        )


class DeepSeekSession:
    """Controls the generation lifecycle and instances of the DeepSeek Client via OpenAI SDK."""

    def __init__(self, config: DeepSeekConfig):
        self.config = config
        self._client = None
        self._http_client: Optional[httpx.Client] = None

    def initialize(self) -> None:
        if not self.config.api_key:
            logger.error("DeepSeek setup aborted: API Key configuration is missing.")
            raise DeepSeekAuthenticationError("An API Key must be supplied to establish a DeepSeek Session.")

        OpenAI = _import_openai()
        try:
            self._http_client = httpx.Client(
                timeout=httpx.Timeout(float(self.config.timeout_seconds)),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
            )
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url="https://api.deepseek.com",
                http_client=self._http_client,
                max_retries=0
            )
            logger.info("DeepSeek network subsystem initiated successfully via compatible SDK.")
        except Exception as e:
            self.shutdown()
            logger.error(f"Failed to provision DeepSeek clients: {str(e)}")
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
                logger.warning(f"Exception managed during DeepSeek client cleanup: {str(e)}")

        if self._http_client:
            try:
                self._http_client.close()
            except Exception as e:
                logger.warning(f"Exception managed during HTTP transport cleanup: {str(e)}")

        self._client = None
        self._http_client = None
        logger.info("DeepSeek background connection pools flushed and decommissioned.")
