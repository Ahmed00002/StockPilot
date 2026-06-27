# ai/providers/openrouter_session.py
import logging
import httpx
from typing import Optional

from .openrouter_config import OpenRouterConfig
from .openrouter_errors import OpenRouterAuthenticationError

logger = logging.getLogger("OpenRouterSession")


def _import_openai():
    """Lazily import the openai SDK (used for OpenRouter compatibility)."""
    try:
        from openai import OpenAI
        return OpenAI
    except ImportError:
        raise ImportError(
            "The 'openai' package is not installed.\n"
            "Install it with:  pip install openai"
        )


class OpenRouterSession:
    """Manages reusable transport layers and OpenRouter API wrappers efficiently."""

    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self._client = None
        self._http_client: Optional[httpx.Client] = None

    def initialize(self) -> None:
        if not self.config.api_key:
            logger.error("OpenRouter Gateway setup rejected: API key parameter missing.")
            raise OpenRouterAuthenticationError("An active API key structure must be present to connect to OpenRouter.")

        OpenAI = _import_openai()
        try:
            self._http_client = httpx.Client(
                timeout=httpx.Timeout(float(self.config.timeout_seconds)),
                limits=httpx.Limits(max_connections=50, max_keepalive_connections=10)
            )
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url="https://openrouter.ai/api/v1",
                http_client=self._http_client,
                max_retries=0,
                default_headers={
                    "HTTP-Referer": "https://stockpilot.ai",
                    "X-Title": "StockPilot Enterprise Architecture"
                }
            )
            logger.info("OpenRouter network interface subsystems mapped and connected.")
        except Exception as e:
            self.shutdown()
            logger.error(f"Failed to provision OpenRouter network stack: {str(e)}")
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
                logger.warning(f"Error captured during OpenRouter client tear-down: {str(e)}")

        if self._http_client:
            try:
                self._http_client.close()
            except Exception as e:
                logger.warning(f"Error captured during OpenRouter HTTP channel extraction: {str(e)}")

        self._client = None
        self._http_client = None
        logger.info("OpenRouter persistent network allocations disassembled cleanly.")
