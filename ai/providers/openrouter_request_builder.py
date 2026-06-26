# ai/providers/openrouter_request_builder.py
import base64
import logging
from typing import Dict, Any, List
from ai.models import AIRequest
from .openrouter_models import OpenRouterModelMeta
from .openrouter_errors import OpenRouterCapabilityError

logger = logging.getLogger("OpenRouterRequestBuilder")

class OpenAIRequestBuilder:
    """Standardizes request structural transformations targeting the generic OpenRouter schema endpoint format."""

    @staticmethod
    def build_payload(request: AIRequest, model_meta: OpenRouterModelMeta) -> Dict[str, Any]:
        """Translates basic framework execution profiles into functional request structures."""
        
        if request.image_data and not model_meta.supports_vision:
            raise OpenRouterCapabilityError(f"OpenRouter Model '{model_meta.id}' does not support vision parameters.")

        messages: List[Dict[str, Any]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        if request.image_data:
            user_content: List[Dict[str, Any]] = [{"type": "text", "text": request.prompt}]
            base64_image = base64.b64encode(request.image_data).decode("utf-8")
            
            mime_type = "image/jpeg"
            header = request.image_data[:16]
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                mime_type = "image/png"
            elif header.startswith(b'RIFF') and b'WEBP' in header[8:12]:
                mime_type = "image/webp"
                
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            })
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": request.prompt})

        payload: Dict[str, Any] = {
            "model": model_meta.id,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if "response_format" in request.additional_parameters:
            if request.additional_parameters["response_format"].get("type") == "json_object" and not model_meta.supports_json:
                logger.warning(f"JSON schema requested but target model '{model_meta.id}' lacks structured features. Bypassing safely.")
            else:
                payload["response_format"] = request.additional_parameters["response_format"]

        return payload