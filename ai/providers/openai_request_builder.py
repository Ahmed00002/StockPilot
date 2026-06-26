# ai/providers/openai_request_builder.py
import base64
import logging
from typing import List, Dict, Any
from ai.models import AIRequest

logger = logging.getLogger("OpenAIRequestBuilder")

class OpenAIRequestBuilder:
    """Translates generic application AIRequest metadata payloads into explicit structural OpenAI SDK input bodies."""

    @staticmethod
    def build_payload(request: AIRequest, default_model: str) -> Dict[str, Any]:
        """Maps an abstract model request onto valid parameter payloads accepted by the completions endpoint."""
        model = request.additional_parameters.get("model", default_model)
        
        messages: List[Dict[str, Any]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        if request.image_data:
            user_content: List[Dict[str, Any]] = [{"type": "text", "text": request.prompt}]
            base64_image = base64.b64encode(request.image_data).decode("utf-8")
            
            # Detect MIME type from magic bytes to prevent SDK rejections for PNGs/WebPs hardcoded as JPEGs
            mime_type = "image/jpeg"
            header = request.image_data[:16]
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                mime_type = "image/png"
            elif header.startswith(b'RIFF') and b'WEBP' in header[8:12]:
                mime_type = "image/webp"
            elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
                mime_type = "image/gif"
                
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
            "model": model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        if "response_format" in request.additional_parameters:
            payload["response_format"] = request.additional_parameters["response_format"]

        return payload