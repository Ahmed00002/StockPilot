# ai/providers/gemini_provider.py
import logging
import time
from datetime import datetime

import google.generativeai as genai
from ai.providers.base_provider import BaseProvider
from ai.models import (
    AIRequest, 
    AIResponse, 
    HealthStatus, 
    ProviderInformation, 
    TokenUsage, 
    CostEstimate
)

from .gemini_config import GeminiConfig
from .gemini_session import GeminiSession
from .gemini_request_builder import GeminiRequestBuilder
from .gemini_response_parser import GeminiResponseParser
from .gemini_rate_limit import GeminiRateLimiter
from .gemini_errors import GeminiErrorMapper, GeminiRateLimitError

logger = logging.getLogger("GeminiProvider")

class GeminiProvider(BaseProvider):
    """Google Gemini specific implementation of the BaseProvider interface."""

    def __init__(self, config: GeminiConfig = None):
        self.config = config or GeminiConfig()
        self.session = GeminiSession(self.config)
        self.rate_limiter = GeminiRateLimiter()
        self.active_requests = set()

    def initialize(self) -> None:
        logger.info("Initializing Gemini Provider...")
        self.session.initialize()

    def shutdown(self) -> None:
        logger.info("Shutting down Gemini Provider...")
        self.session.shutdown()
        self.active_requests.clear()

    def authenticate(self) -> bool:
        return self.validate_credentials()

    def validate_credentials(self) -> bool:
        if not self.config.api_key or len(self.config.api_key) < 20:
            logger.error("Invalid or missing Gemini API key format.")
            return False
            
        try:
            self.session.initialize()
            # A lightweight call to verify the key
            list(genai.list_models())
            return True
        except Exception as e:
            logger.error(f"Gemini API key validation failed: {str(e)}")
            return False

    def health_check(self) -> HealthStatus:
        start_time = time.time()
        is_healthy = False
        error_msg = None
        
        try:
            self.validate_credentials()
            is_healthy = True
        except Exception as e:
            error_msg = str(e)
            
        latency = (time.time() - start_time) * 1000
        
        return HealthStatus(
            is_healthy=is_healthy,
            latency_ms=latency,
            last_checked=datetime.now(),
            error_message=error_msg
        )

    def _execute_request_with_retry(self, model_name: str, content: list, generation_config: genai.types.GenerationConfig) -> AIResponse:
        model = self.session.get_model(model_name)
        safety_settings = GeminiRequestBuilder.build_safety_settings()
        
        for attempt in range(self.config.max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                
                start_time = time.time()
                response = model.generate_content(
                    content,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                execution_time = (time.time() - start_time) * 1000
                
                return GeminiResponseParser.parse(response, model_name, execution_time)
                
            except Exception as e:
                mapped_error = GeminiErrorMapper.map_exception(e)
                
                if isinstance(mapped_error, GeminiRateLimitError):
                    self.rate_limiter.trigger_cooldown(10.0 * (attempt + 1))
                    
                if attempt == self.config.max_retries - 1:
                    logger.error(f"Gemini request failed after {self.config.max_retries} attempts. Final error: {mapped_error}")
                    raise mapped_error
                    
                logger.warning(f"Gemini request attempt {attempt + 1} failed. Retrying... ({str(mapped_error)})")
                time.sleep(self.config.retry_delay_seconds * (attempt + 1))

    def vision_request(self, request: AIRequest) -> AIResponse:
        logger.info("Executing Gemini Vision Request")
        model_name = request.additional_parameters.get("model", self.config.default_vision_model)
        content = GeminiRequestBuilder.build_vision_content(request)
        config = GeminiRequestBuilder.build_generation_config(request)
        
        return self._execute_request_with_retry(model_name, content, config)

    def text_request(self, request: AIRequest) -> AIResponse:
        logger.info("Executing Gemini Text Request")
        model_name = request.additional_parameters.get("model", self.config.default_text_model)
        content = GeminiRequestBuilder.build_text_content(request)
        config = GeminiRequestBuilder.build_generation_config(request)
        
        return self._execute_request_with_retry(model_name, content, config)

    def cancel_request(self, request_id: str) -> bool:
        # The Python SDK for Gemini currently does not support async request cancellation.
        # Implemented for interface compliance.
        logger.warning(f"Cancellation of active Gemini requests is not supported by the SDK. (Request: {request_id})")
        return False

    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        try:
            model_name = request.additional_parameters.get("model", self.config.default_text_model)
            model = self.session.get_model(model_name)
            
            content = GeminiRequestBuilder.build_vision_content(request) if request.image_data else GeminiRequestBuilder.build_text_content(request)
            
            response = model.count_tokens(content)
            
            return TokenUsage(
                prompt_tokens=response.total_tokens,
                response_tokens=0,
                total_tokens=response.total_tokens
            )
        except Exception as e:
            logger.warning(f"Failed to estimate Gemini tokens: {str(e)}")
            return TokenUsage()

    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        # Costs vary heavily by model. Implementation depends on external pricing logic.
        # Returning a zeroed object as pricing shouldn't be hardcoded in the provider core.
        return CostEstimate(currency="USD", amount=0.0)

    def get_provider_information(self) -> ProviderInformation:
        return ProviderInformation(
            name="Google Gemini",
            version="1.0",
            supported_models=self.config.supported_models,
            capabilities=["text", "vision", "safety_filtering"]
        )