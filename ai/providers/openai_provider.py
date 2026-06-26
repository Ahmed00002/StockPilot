# ai/providers/openai_provider.py
import logging
import time
from datetime import datetime

from ai.providers.base_provider import BaseProvider
from ai.models import (
    AIRequest, 
    AIResponse, 
    HealthStatus, 
    ProviderInformation, 
    TokenUsage, 
    CostEstimate
)

from .openai_config import OpenAIConfig
from .openai_session import OpenAISession
from .openai_request_builder import OpenAIRequestBuilder
from .openai_response_parser import OpenAIResponseParser
from .openai_rate_limit import OpenAIRateLimiter
from .openai_errors import OpenAIErrorMapper, OpenAIRateLimitError

logger = logging.getLogger("OpenAIProvider")

class OpenAIProvider(BaseProvider):
    """OpenAI custom implementation conforming to the core BaseProvider system blueprint."""

    def __init__(self, config: OpenAIConfig = None):
        self.config = config or OpenAIConfig()
        self.session = OpenAISession(self.config)
        self.rate_limiter = OpenAIRateLimiter()

    def initialize(self) -> None:
        logger.info("Initializing OpenAI Provider Engine resources...")
        self.session.initialize()

    def shutdown(self) -> None:
        logger.info("Decommissioning active OpenAI Provider interface allocations...")
        self.session.shutdown()

    def authenticate(self) -> bool:
        return self.validate_credentials()

    def validate_credentials(self) -> bool:
        if not self.config.api_key or not self.config.api_key.startswith("sk-"):
            logger.error("OpenAI verification failure: API key format structural invalidity.")
            return False
            
        try:
            client = self.session.get_client()
            # Issue a minimal metadata retrieval request to guarantee token usability
            client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI structural identity verification rejected by remote service: {str(e)}")
            return False

    def health_check(self) -> HealthStatus:
        start_time = time.time()
        is_healthy = False
        error_msg = None
        
        try:
            is_healthy = self.validate_credentials()
            if not is_healthy:
                error_msg = "Credentials failed identity validation tests."
        except Exception as e:
            error_msg = str(e)
            
        latency = (time.time() - start_time) * 1000
        
        return HealthStatus(
            is_healthy=is_healthy,
            latency_ms=latency,
            last_checked=datetime.now(),
            error_message=error_msg
        )

    def _execute_with_retry_loop(self, request: AIRequest, default_model: str) -> AIResponse:
        client = self.session.get_client()
        payload = OpenAIRequestBuilder.build_payload(request, default_model)
        
        # Max attempts must be at least 1, otherwise a 0 retry configuration bypasses execution entirely.
        max_attempts = max(1, self.config.max_retries + 1)
        
        for attempt in range(max_attempts):
            try:
                self.rate_limiter.wait_if_needed()
                
                start_time = time.time()
                raw_response = client.chat.completions.create(**payload)
                execution_time = (time.time() - start_time) * 1000
                
                return OpenAIResponseParser.parse(raw_response, execution_time)
                
            except Exception as e:
                mapped_error = OpenAIErrorMapper.map_exception(e)
                
                if isinstance(mapped_error, OpenAIRateLimitError):
                    self.rate_limiter.enforce_cooldown(15.0 * (attempt + 1))
                    
                if attempt == max_attempts - 1:
                    logger.error(f"OpenAI endpoint execution exhausted all {max_attempts} attempts. Terminal failure: {str(mapped_error)}")
                    raise mapped_error
                    
                logger.warning(f"OpenAI execution attempt {attempt + 1} failed. Retrying... Trace: {str(mapped_error)}")
                time.sleep(self.config.retry_delay_seconds * (attempt + 1))

    def vision_request(self, request: AIRequest) -> AIResponse:
        logger.info("Routing incoming request structure toward OpenAI Vision pipelines.")
        return self._execute_with_retry_loop(request, self.config.default_vision_model)

    def text_request(self, request: AIRequest) -> AIResponse:
        logger.info("Routing incoming request structure toward OpenAI Text pipelines.")
        return self._execute_with_retry_loop(request, self.config.default_text_model)

    def cancel_request(self, request_id: str) -> bool:
        logger.warning(f"Synchronous runtime pipeline execution does not process dynamic cancellations natively (ID: {request_id}).")
        return False

    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        # Estimation assumes standard character ratios when full local tokenizers are unassigned
        base_estimate = len(request.prompt) // 4
        if request.image_data:
            base_estimate += 765 # Fixed high-res base cost estimation for OpenAI tiles
        return TokenUsage(prompt_tokens=base_estimate, response_tokens=0, total_tokens=base_estimate)

    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        return CostEstimate(currency="USD", amount=0.0)

    def get_provider_information(self) -> ProviderInformation:
        return ProviderInformation(
            name="OpenAI Engine",
            version="1.0.0",
            supported_models=self.config.supported_models,
            capabilities=["text", "vision", "structured_json"]
        )