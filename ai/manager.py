# ai/manager.py
import logging
from typing import Optional

from ai.provider_manager import ProviderManager
from ai.models import AIRequest, AIResponse
from ai.request_context import RequestContext

logger = logging.getLogger("AIManager")

class AIManager:
    """
    High-level facade for the AI subsystem.
    Handles the execution of requests by routing them to the appropriate providers
    and returning normalized results to the application layer.
    """

    def __init__(self, provider_manager: ProviderManager) -> None:
        self._provider_manager = provider_manager

    def execute_request(self, provider_name: str, context: RequestContext) -> AIResponse:
        """
        Executes a normalized request against the specified provider.
        
        Args:
            provider_name: The name of the configured provider to use.
            context: The RequestContext containing domain data and settings.
            
        Returns:
            AIResponse: The normalized response from the AI provider.
            
        Raises:
            ValueError: If the provider is unavailable or disabled.
            RuntimeError: If the execution fails unexpectedly.
        """
        provider = self._provider_manager.get_provider(provider_name)
        if not provider:
            logger.error(f"Cannot execute request: Provider '{provider_name}' is not available.")
            raise ValueError(f"Provider '{provider_name}' is not available or disabled.")

        request = self._build_ai_request(context)
        
        try:
            logger.info(f"Executing AI request via provider '{provider_name}'.")
            
            # INTEGRATION FIX: Defer heavy File IO to the execution phase. 
            # Prevents main-thread UI blocking prior to orchestration background dispatch.
            if context.image_path and context.image_path.exists():
                try:
                    with open(context.image_path, "rb") as img_file:
                        request.image_data = img_file.read()
                except IOError as e:
                    logger.error(f"Failed to read image at {context.image_path}: {e}")

            if request.image_data is not None:
                response = provider.vision_request(request)
            else:
                response = provider.text_request(request)
                
            logger.info(f"Request execution successful via '{provider_name}'.")
            return response
            
        except Exception as e:
            logger.error(f"Error executing request on '{provider_name}': {str(e)}")
            raise RuntimeError(f"AI Request execution failed: {str(e)}") from e

    def _build_ai_request(self, context: RequestContext) -> AIRequest:
        """
        Converts a domain-level RequestContext into an infrastructure-level AIRequest.
        
        Args:
            context: The domain request context.
            
        Returns:
            AIRequest: Formatted request ready for a provider.
        """
        return AIRequest(
            prompt=context.prompt,
            system_prompt=context.get_setting("system_prompt", None),
            image_data=None, # INTEGRATION FIX: Deferred to execute_request
            temperature=context.temperature,
            max_tokens=context.max_tokens,
            timeout_seconds=context.timeout,
            additional_parameters=context.user_settings
        )