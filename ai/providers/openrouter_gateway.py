# ai/providers/openrouter_gateway.py
import logging
import httpx
from datetime import datetime
from typing import List, Optional

from ai.models import AIRequest
from .openrouter_config import OpenRouterConfig
from .openrouter_models import OpenRouterModelMeta
from .openrouter_model_registry import OpenRouterModelRegistry
from .openrouter_errors import OpenRouterGatewayError

logger = logging.getLogger("OpenRouterGateway")

class OpenRouterGateway:
    """Coordinates automated background discovery pipelines and caching for hundreds of remote models."""

    def __init__(self, config: OpenRouterConfig, registry: OpenRouterModelRegistry):
        self.config = config
        self.registry = registry

    def discover_models(self) -> bool:
        """Polls the remote gateway manifest to parse model capabilities and update internal registries."""
        logger.info("Querying OpenRouter metadata service for available routing arrays...")
        url = "https://openrouter.ai/api/v1/models"
        
        try:
            headers = {}
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
                
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=headers)
                
            if response.status_code != 200:
                logger.error(f"OpenRouter discovery failure. Server responded with state: {response.status_code}")
                return False
                
            data = response.json()
            models_list = data.get("data", [])
            discovered: List[OpenRouterModelMeta] = []
            
            for item in models_list:
                model_id = item.get("id")
                if not model_id or model_id in self.config.disabled_models:
                    continue
                    
                # Deconstruct naming rules to locate logical remote provider assignments
                provider_parts = model_id.split("/")
                provider_name = provider_parts[0] if len(provider_parts) > 1 else "unknown"
                
                context_length = int(item.get("context_length", 2048))
                
                pricing = item.get("pricing", {})
                # Normalize cost configurations to absolute per-token amounts (from string metadata)
                try:
                    input_cost = float(pricing.get("prompt", "0.0"))
                    output_cost = float(pricing.get("completion", "0.0"))
                except ValueError:
                    input_cost = 0.0
                    output_cost = 0.0
                    
                architecture = item.get("architecture", {})
                modality = architecture.get("modality", "text")
                
                # Deduce structural capability markers based on parameters and configurations
                supports_vision = "image" in modality or "multimodal" in modality
                supports_tools = "tools" in item or "function_calling" in architecture.get("instruct_type", "")
                supports_reasoning = "reasoning" in model_id.lower() or "cot" in model_id.lower()
                
                meta = OpenRouterModelMeta(
                    id=model_id,
                    name=item.get("name", model_id),
                    provider=provider_name,
                    context_length=context_length,
                    input_cost_per_token=input_cost,
                    output_cost_per_token=output_cost,
                    supports_vision=supports_vision,
                    supports_streaming=True,  # OpenRouter universally supports server-sent streaming channels
                    supports_json="json" in model_id.lower() or supports_tools,
                    supports_tools=supports_tools,
                    supports_reasoning=supports_reasoning,
                    last_updated=datetime.now()
                )
                discovered.append(meta)
                
            if discovered:
                self.registry.update_registry(discovered)
                return True
                
            return False
        except Exception as e:
            logger.error(f"Uncaught anomaly identified during runtime model discovery: {str(e)}")
            return False

    def select_intelligent_route(self, request: AIRequest, required_capability: Optional[str] = None) -> OpenRouterModelMeta:
        """Evaluates automated metrics to output the best tracking target option for complex layouts."""
        pref = self.config.routing_preference
        
        # Pull model overrides explicitly from current incoming parameter attributes
        model_override = request.additional_parameters.get("model")
        if model_override:
            meta = self.registry.get_model(model_override)
            if meta:
                return meta

        all_valid = self.registry.get_all_models()
        if not all_valid:
            # Revisit cache layers if empty on initial calls
            self.discover_models()
            all_valid = self.registry.get_all_models()
            if not all_valid:
                raise OpenRouterGatewayError("Registry catalog tracking states are empty. Gateway route aborted.")

        if required_capability:
            from .openrouter_capabilities import OpenRouterCapabilities
            all_valid = [m for m in all_valid if OpenRouterCapabilities.verify_capability(m, required_capability)]

        if not all_valid:
            # Fallback directly to generic configurations if specialized capabilities turn up empty
            fallback = self.registry.get_model(self.config.fallback_model)
            if fallback:
                return fallback
            raise OpenRouterGatewayError(f"No functional open router model variants matched capability '{required_capability}'.")

        if pref == "cheapest":
            all_valid.sort(key=lambda m: (m.input_cost_per_token + m.output_cost_per_token))
            return all_valid[0]
        elif pref == "highest_context":
            all_valid.sort(key=lambda m: m.context_length, reverse=True)
            return all_valid[0]
            
        # Default strategy handles standard tracking matching checks
        configured_default = self.registry.get_model(self.config.default_model)
        if configured_default:
            return configured_default
            
        return all_valid[0]
