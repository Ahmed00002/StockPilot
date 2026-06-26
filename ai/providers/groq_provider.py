# ai/providers/groq_provider.py
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

from .groq_config import GroqConfig
from .groq_session import GroqSession
from .groq_request_builder import GroqRequestBuilder
from .groq_response_parser import GroqResponseParser
from .groq_rate_limit import GroqRateLimiter
from .groq_errors import GroqErrorMapper, GroqRateLimitError

logger = logging.getLogger("GroqProvider")

class GroqProvider(BaseProvider):
    """Groq custom implementation conforming to the core BaseProvider system blueprint."""

    def __init__(self, config: GroqConfig = None):
        self.config = config or GroqConfig()
        self.session = GroqSession(self.config)
        self.rate_limiter = GroqRateLimiter()

    def initialize(self) -> None:
        logger.info("Initializing Groq Provider Engine resources...")
        self.session.initialize()

    def shutdown(self) -> None:
        logger.info("Decommissioning active Groq Provider interface allocations...")
        self.session.shutdown()

    def authenticate(self) -> bool:
        return self.validate_credentials()

    def validate_credentials(self) -> bool:
        if not self.config.api_key or not self.config.api_key.startswith("gsk_"):
            logger.error("Groq verification failure: API key format structural invalidity.")
            return False
            
        try:
            client = self.session.get_client()
            client.models.list()
            return True
        except Exception as e:
            logger.error(f"Groq identity verification rejected by remote service: {str(e)}")
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
        payload = GroqRequestBuilder.build_payload(request, default_model)
        
        max_attempts = max(1, self.config.max_retries + 1)
        
        for attempt in range(max_attempts):
            try:
                self.rate_limiter.wait_if_needed()
                
                start_time = time.time()
                raw_response = client.chat.completions.create(**payload)
                execution_time = (time.time() - start_time) * 1000
                
                return GroqResponseParser.parse(raw_response, execution_time)
                
            except Exception as e:
                mapped_error = GroqErrorMapper.map_exception(e)
                
                if isinstance(mapped_error, GroqRateLimitError):
                    self.rate_limiter.enforce_cooldown(15.0 * (attempt + 1))
                    
                if attempt == max_attempts - 1:
                    logger.error(f"Groq endpoint execution exhausted {max_attempts} attempts. Terminal failure: {str(mapped_error)}")
                    raise mapped_error
                    
                logger.warning(f"Groq execution attempt {attempt + 1} failed. Retrying... Trace: {str(mapped_error)}")
                time.sleep(self.config.retry_delay_seconds * (attempt + 1))

    def vision_request(self, request: AIRequest) -> AIResponse:
        logger.info("Routing incoming request structure toward Groq Vision pipelines.")
        return self._execute_with_retry_loop(request, self.config.default_vision_model)

    def text_request(self, request: AIRequest) -> AIResponse:
        logger.info("Routing incoming request structure toward Groq Text pipelines.")
        return self._execute_with_retry_loop(request, self.config.default_text_model)

    def cancel_request(self, request_id: str) -> bool:
        logger.warning(f"Synchronous Groq pipeline execution does not process dynamic cancellations (ID: {request_id}).")
        return False

    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        base_estimate = len(request.prompt) // 4
        if request.image_data:
            base_estimate += 1000
        return TokenUsage(prompt_tokens=base_estimate, response_tokens=0, total_tokens=base_estimate)

    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        return CostEstimate(currency="USD", amount=0.0)

    def get_provider_information(self) -> ProviderInformation:
        return ProviderInformation(
            name="Groq LPU Engine",
            version="1.0.0",
            supported_models=self.config.supported_models,
            capabilities=["text", "vision", "structured_json"]
        )