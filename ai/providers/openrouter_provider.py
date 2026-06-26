# ai/providers/openrouter_provider.py
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

from .openrouter_config import OpenRouterConfig
from .openrouter_session import OpenRouterSession
from .openrouter_model_registry import OpenRouterModelRegistry
from .openrouter_gateway import OpenRouterGateway
from .openrouter_request_builder import OpenAIRequestBuilder
from .openrouter_response_parser import OpenRouterResponseParser
from .openrouter_rate_limit import OpenRouterRateLimiter
from .openrouter_errors import OpenRouterErrorMapper, OpenRouterRateLimitError

logger = logging.getLogger("OpenRouterProvider")

class OpenRouterProvider(BaseProvider):
    """Unified OpenRouter AI Gateway provider wrapper managing hundreds of target models."""

    def __init__(self, config: OpenRouterConfig = None):
        self.config = config or OpenRouterConfig()
        self.registry = OpenRouterModelRegistry()
        self.session = OpenRouterSession(self.config)
        self.gateway = OpenRouterGateway(self.config, self.registry)
        self.rate_limiter = OpenRouterRateLimiter()

    def initialize(self) -> None:
        logger.info("Initializing OpenRouter AI Gateway core system modules...")
        self.session.initialize()
        # Prime discovery arrays asynchronously or during early lifecycle boot phases
        self.gateway.discover_models()

    def shutdown(self) -> None:
        logger.info("Decommissioning active OpenRouter gateway tracking allocations...")
        self.session.shutdown()

    def authenticate(self) -> bool:
        return self.validate_credentials()

    def validate_credentials(self) -> bool:
        if not self.config.api_key:
            return False
        try:
            client = self.session.get_client()
            # Simple metadata query acts as authenticating handshake validation verification
            client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenRouter identity validation rejected by endpoint: {str(e)}")
            return False

    def health_check(self) -> HealthStatus:
        start_time = time.time()
        is_healthy = False
        error_msg = None
        
        try:
            is_healthy = self.validate_credentials()
            if is_healthy:
                # Confirm registry structures are intact or populating accurately
                if not self.registry.get_all_models():
                    self.gateway.discover_models()
            else:
                error_msg = "Gateway authentication tokens failed structural sanity test patterns."
        except Exception as e:
            error_msg = str(e)
            
        latency = (time.time() - start_time) * 1000
        
        return HealthStatus(
            is_healthy=is_healthy,
            latency_ms=latency,
            last_checked=datetime.now(),
            error_message=error_msg
        )

    def _execute_gateway_request(self, request: AIRequest, required_capability: str) -> AIResponse:
        client = self.session.get_client()
        
        # Route processing target selection down to optimal configured models
        selected_model_meta = self.gateway.select_intelligent_route(request, required_capability)
        payload = OpenAIRequestBuilder.build_payload(request, selected_model_meta)
        
        max_attempts = max(1, self.config.max_retries + 1)
        
        for attempt in range(max_attempts):
            try:
                self.rate_limiter.wait_if_needed()
                
                start_time = time.time()
                raw_response = client.chat.completions.create(**payload)
                execution_time = (time.time() - start_time) * 1000
                
                return OpenRouterResponseParser.parse(raw_response, selected_model_meta, execution_time)
                
            except Exception as e:
                mapped_error = OpenRouterErrorMapper.map_exception(e)
                
                if isinstance(mapped_error, OpenRouterRateLimitError):
                    self.rate_limiter.enforce_cooldown(20.0 * (attempt + 1))
                    
                if attempt == max_attempts - 1:
                    logger.error(f"OpenRouter Gateway dispatch exhausted all retries. Terminal state: {str(mapped_error)}")
                    raise mapped_error
                    
                logger.warning(f"OpenRouter attempt {attempt + 1} failed. Retrying... Code: {str(mapped_error)}")
                time.sleep(self.config.retry_delay_seconds * (attempt + 1))

    def vision_request(self, request: AIRequest) -> AIResponse:
        logger.info("Passing vision request parameters into OpenRouter routing arrays.")
        return self._execute_gateway_request(request, "vision")

    def text_request(self, request: AIRequest) -> AIResponse:
        logger.info("Passing text query elements into OpenRouter routing arrays.")
        capability = "reasoning" if request.additional_parameters.get("use_reasoner") else "text"
        return self._execute_gateway_request(request, capability)

    def cancel_request(self, request_id: str) -> bool:
        logger.warning(f"Synchronous gateway pipeline components cannot cancel dynamic request id tasks: {request_id}")
        return False

    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        base_estimate = len(request.prompt) // 4
        return TokenUsage(prompt_tokens=base_estimate, response_tokens=0, total_tokens=base_estimate)

    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        # Provider context handles cost calculation inline within the custom response parser block
        return CostEstimate(currency="USD", amount=0.0)

    def get_provider_information(self) -> ProviderInformation:
        models = [m.id for m in self.registry.get_all_models()]
        return ProviderInformation(
            name="OpenRouter Gateway System",
            version="2.1.0",
            supported_models=models if models else self.config.pinned_models,
            capabilities=["text", "vision", "structured_json", "reasoning", "multiplex_routing"]
        )