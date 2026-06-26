# ai/providers/base_provider.py
from abc import ABC, abstractmethod
from typing import Optional

from ai.models import (
    AIRequest, 
    AIResponse, 
    HealthStatus, 
    ProviderInformation, 
    TokenUsage, 
    CostEstimate
)

class BaseProvider(ABC):
    """
    Abstract base class for all AI Providers.
    Defines the standard contract that every provider implementation must fulfill.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initializes the provider, allocating necessary local resources."""
        raise NotImplementedError("Provider must implement initialize()")

    @abstractmethod
    def shutdown(self) -> None:
        """Shuts down the provider, releasing all allocated resources."""
        raise NotImplementedError("Provider must implement shutdown()")

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticates the provider with the underlying service.
        
        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        raise NotImplementedError("Provider must implement authenticate()")

    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validates the currently configured credentials locally without a full connection.
        
        Returns:
            bool: True if credentials format/presence is valid.
        """
        raise NotImplementedError("Provider must implement validate_credentials()")

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """
        Pings the provider service to determine operational status.
        
        Returns:
            HealthStatus: The current health and latency of the provider.
        """
        raise NotImplementedError("Provider must implement health_check()")

    @abstractmethod
    def vision_request(self, request: AIRequest) -> AIResponse:
        """
        Executes a multimodal request containing image data.
        
        Args:
            request: The AIRequest containing image bytes and prompts.
            
        Returns:
            AIResponse: The normalized response from the model.
        """
        raise NotImplementedError("Provider must implement vision_request()")

    @abstractmethod
    def text_request(self, request: AIRequest) -> AIResponse:
        """
        Executes a purely text-based generation request.
        
        Args:
            request: The AIRequest containing text prompts.
            
        Returns:
            AIResponse: The normalized response from the model.
        """
        raise NotImplementedError("Provider must implement text_request()")

    @abstractmethod
    def cancel_request(self, request_id: str) -> bool:
        """
        Attempts to cancel an ongoing network request.
        
        Args:
            request_id: The unique identifier of the active request.
            
        Returns:
            bool: True if successfully cancelled, False otherwise.
        """
        raise NotImplementedError("Provider must implement cancel_request()")

    @abstractmethod
    def estimate_tokens(self, request: AIRequest) -> TokenUsage:
        """
        Estimates the token count for a given request before execution.
        
        Args:
            request: The target AIRequest.
            
        Returns:
            TokenUsage: The estimated prompt tokens.
        """
        raise NotImplementedError("Provider must implement estimate_tokens()")

    @abstractmethod
    def estimate_cost(self, tokens: TokenUsage) -> CostEstimate:
        """
        Calculates the financial cost for a given token volume based on provider pricing.
        
        Args:
            tokens: The usage statistics.
            
        Returns:
            CostEstimate: The calculated monetary cost.
        """
        raise NotImplementedError("Provider must implement estimate_cost()")

    @abstractmethod
    def get_provider_information(self) -> ProviderInformation:
        """
        Retrieves the static capabilities and identity of the provider.
        
        Returns:
            ProviderInformation: The definition of the provider.
        """
        raise NotImplementedError("Provider must implement get_provider_information()")