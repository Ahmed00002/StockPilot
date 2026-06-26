# ai/providers/deepseek_provider.py
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

from .deepseek_config import DeepSeekConfig
from .deepseek_session import DeepSeekSession
from .deepseek_request_builder import DeepSeekRequestBuilder
from .deepseek_response_parser import DeepSeekResponseParser
from .deepseek_rate_limit import DeepSeekRateLimiter
from .deepseek_errors import DeepSeekErrorMapper, DeepSeekRateLimitError, DeepSeekCapabilityError

logger = logging.getLogger("DeepSeekProvider")

class DeepSeekProvider(BaseProvider):
    """DeepSeek custom implementation conforming to the core BaseProvider system blueprint."""

    def __init__(self, config: DeepSeekConfig = None):
        self.config = config or DeepSeekConfig()
        self.session = DeepSeekSession(self.config)
        self.rate_limiter = DeepSeekRateLimiter()

    def initialize(self) -> None:
        logger.info("Initializing DeepSeek Provider Engine resources...")
        self.session.initialize()

    def shutdown(self) -> None:
        logger.info("Decommissioning active DeepSeek Provider interface allocations...")
        self.session.shutdown()

    def authenticate(self) -> bool:
        return self.validate_credentials()

    def validate_credentials(self) -> bool:
        if not self.config.api_key or not self.config.api_key.startswith("sk-"):
            logger.error("DeepSeek verification failure: API key format structural invalidity.")
            return False
            
        try:
            client = self.session.get_client()
            client.models.list()
            return True
        except Exception as e:
            logger.error(f"DeepSeek identity verification rejected by remote service: {str(e)}")
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
        payload = DeepSeekRequestBuilder.build_payload(request, default_model)
        
        max_attempts = max(1, self.config.max_retries + 1)
        
        for attempt in range(max_attempts):
            try:
                self.rate_limiter.wait_if_needed()
                
                start_time = time.time()
                raw_response = client.chat.completions.create(**payload)
                execution_time = (time.time() - start_time) * 1000
                
                return DeepSeekResponseParser.parse(raw_response, execution_time)
                
            except Exception as e:
                mapped_error = DeepSeekErrorMapper.map_exception(e)
                
                if isinstance(mapped_error, DeepSeekRateLimitError):
                    self.rate_limiter.enforce_cooldown(15.0 * (attempt + 1))
                    
                if attempt == max_attempts - 1:
                    logger.error(f"DeepSeek endpoint execution exhausted {max_attempts} attempts. Terminal failure: {str(mapped_error)}")
                    raise mapped_error
                    
                logger.warning(f"DeepSeek execution attempt {attempt + 1} failed. Retrying... Trace: {str(mapped_error)}")
                time.sleep(self.config.retry_delay_seconds * (attempt + 1))

    def vision_request(self, request: AIRequest) -> AIResponse:
        logger.error("DeepSeek does not natively support multimodal vision requests.")
        raise DeepSeekCapabilityError("Vision request rejected. DeepSeek API currently lacks multimodal image processing.")

    def text_request(self, request: AIRequest) -> AIResponse:
        logger.info("Routing incoming request structure toward DeepSeek Text pipelines.")
        # If the request context implies advanced logical planning, shift to reasoner model.
        # This allows flexible utilization of DeepSeek's CoT model if specified in parameters.
        model = self.config.default_text_model
        if request.additional_parameters.get("use_reasoner", False):
            model = self.config.default_reasoning_model
            
        return self._execute_with_retry_loop(request, model)

    def cancel_request(self, request_id: str) -> bool:
        logger.warning(f"Synchronous DeepSeek pipeline execution does not process dynamic cancellations (ID: {request_id}).")
        return False

    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        base_estimate = len(request.prompt) // 4
        return TokenUsage(prompt_tokens=base_estimate, response_tokens=0, total_tokens=base_estimate)

    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        return CostEstimate(currency="USD", amount=0.0)

    def get_provider_information(self) -> ProviderInformation:
        return ProviderInformation(
            name="DeepSeek",
            version="1.0.0",
            supported_models=self.config.supported_models,
            capabilities=["text", "structured_json", "reasoning"]
        )