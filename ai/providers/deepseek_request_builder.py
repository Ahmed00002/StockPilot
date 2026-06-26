# ai/providers/deepseek_request_builder.py
import logging
from typing import List, Dict, Any
from ai.models import AIRequest
from .deepseek_errors import DeepSeekCapabilityError

logger = logging.getLogger("DeepSeekRequestBuilder")

class DeepSeekRequestBuilder:
    """Translates generic application AIRequest metadata payloads into DeepSeek SDK input bodies."""

    @staticmethod
    def build_payload(request: AIRequest, default_model: str) -> Dict[str, Any]:
        """Maps an abstract model request onto valid parameter payloads accepted by DeepSeek endpoints."""
        model = request.additional_parameters.get("model", default_model)
        
        if request.image_data:
            raise DeepSeekCapabilityError(f"Model '{model}' does not support vision/image inputs. DeepSeek API currently lacks multimodal endpoints.")

        messages: List[Dict[str, str]] = []
        
        # DeepSeek specifically requires system prompts to be handled carefully, 
        # especially for reasoning models where system prompts are not always fully supported or act differently.
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        messages.append({"role": "user", "content": request.prompt})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if "response_format" in request.additional_parameters:
            # Note: DeepSeek-chat supports JSON object format, but deepseek-reasoner does not.
            if model == "deepseek-reasoner" and request.additional_parameters["response_format"].get("type") == "json_object":
                logger.warning(f"JSON mode requested but '{model}' does not support JSON format structurally. Stripping parameter.")
            else:
                payload["response_format"] = request.additional_parameters["response_format"]

        return payload