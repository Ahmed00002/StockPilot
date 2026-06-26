# metadata/vision_request_builder.py
import json
import logging
from typing import Optional, Dict

from ai.models import AIRequest
from ai.prompt.prompt_engine import PromptEngine
from ai.request_context import RequestContext

from .vision_context import VisionContext

logger = logging.getLogger("VisionRequestBuilder")

class VisionRequestBuilder:
    """Translates a domain VisionContext into a structured AIRequest using the Prompt Engine."""

    def __init__(self, prompt_engine: PromptEngine):
        self._prompt_engine = prompt_engine

    def build_request(self, context: VisionContext) -> AIRequest:
        """
        Executes the prompt intelligence pipeline to format constraints and rules
        before creating the raw AIRequest object for the Orchestrator.
        """
        # We explicitly request JSON structured output from compatible providers
        # by appending a strong structural definition to the system prompt via user_prefs
        user_prefs = context.user_preferences.copy()
        
        # Enforce JSON structured generation schema
        json_schema = {
            "title": "string",
            "description": "string",
            "keywords": ["string"],
            "primary_category": "string",
            "secondary_category": "string",
            "detected_objects": ["string"],
            "detected_scene": "string",
            "commercial_intent": {
                "primary_industry": "string",
                "target_audience": "string",
                "concept_tags": ["string"]
            }
        }
        
        user_prefs["response_format"] = {"type": "json_object"}
        user_prefs["system_prompt_append"] = f"You must return ONLY valid JSON matching this schema: {json.dumps(json_schema)}"

        # Convert local IntelligenceReport into prompt context dictionary parameters
        intelligence_data = {
            "width": context.intelligence_report.technical.width,
            "height": context.intelligence_report.technical.height,
            "orientation": context.intelligence_report.technical.aspect_ratio,
            "quality_score": context.intelligence_report.quality.overall_score,
            "dominant_colors": ", ".join([str(c) for c in context.intelligence_report.color.dominant_colors]),
            "image_hash": context.intelligence_report.fingerprint.sha256_hash
        }

        # 1. Execute Prompt Engine pipeline
        final_prompt, system_prompt, validation_report = self._prompt_engine.manager.generate_prompt(
            template_id=context.prompt_template_id,
            workspace=context.workspace,
            language=context.language,
            marketplace=context.marketplace,
            provider=context.provider_name,
            image_path=context.image_path,
            intelligence_data=intelligence_data,
            user_prefs=user_prefs,
            image_hash=intelligence_data["image_hash"]
        )

        if not validation_report.is_valid:
            logger.error(f"Prompt generation failed structural validation: {validation_report.errors}")
            raise ValueError("Vision Prompt validation failed prior to execution.")

        # 2. Append JSON schema requirement to system prompt
        if system_prompt:
            system_prompt += f"\n\n{user_prefs['system_prompt_append']}"
        else:
            system_prompt = user_prefs["system_prompt_append"]

        # 3. Read image bytes
        image_bytes = None
        try:
            with open(context.image_path, "rb") as f:
                image_bytes = f.read()
        except IOError as e:
            logger.error(f"Failed to read image bytes for vision request: {str(e)}")
            raise

        # 4. Construct generic AIRequest
        return AIRequest(
            prompt=final_prompt,
            system_prompt=system_prompt,
            image_data=image_bytes,
            temperature=0.4, # Lower temperature for metadata consistency
            max_tokens=2048,
            additional_parameters=user_prefs
        )