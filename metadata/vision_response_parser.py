# metadata/vision_response_parser.py
import json
import re
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from ai.models import AIResponse
from .metadata_models import GeneratedMetadata, CommercialIntent
from .metadata_formatter import MetadataFormatter

logger = logging.getLogger("VisionResponseParser")

class VisionResponseParser:
    """Transforms normalized generic AI responses containing JSON into strict GeneratedMetadata models."""

    @staticmethod
    def parse(
        response: AIResponse, 
        image_hash: str, 
        marketplace: str, 
        language: str,
        prompt_version: str
    ) -> GeneratedMetadata:
        
        data = VisionResponseParser._extract_json(response.content)
        if not data:
            logger.error("Failed to extract JSON schema from vision response payload.")
            raise ValueError("Vision metadata generation yielded malformed or empty structures.")

        # Extract Raw Fields
        raw_title = data.get("title", "")
        raw_desc = data.get("description", "")
        raw_keywords = data.get("keywords", [])
        
        # Clean & Format
        title = MetadataFormatter.format_title(raw_title)
        desc = MetadataFormatter.format_description(raw_desc)
        keywords = MetadataFormatter.format_keywords(raw_keywords)

        # Commercial Intent Mapping
        intent_raw = data.get("commercial_intent", {})
        intent = CommercialIntent(
            primary_industry=str(intent_raw.get("primary_industry", "")),
            target_audience=str(intent_raw.get("target_audience", "")),
            concept_tags=[str(t) for t in intent_raw.get("concept_tags", [])][:5]
        )

        return GeneratedMetadata(
            id=str(uuid.uuid4()),
            image_hash=image_hash,
            title=title,
            description=desc,
            keywords=keywords,
            primary_category=str(data.get("primary_category", "")),
            secondary_category=str(data.get("secondary_category", "")),
            detected_objects=[str(o) for o in data.get("detected_objects", [])],
            detected_scene=str(data.get("detected_scene", "")),
            commercial_intent=intent,
            marketplace=marketplace,
            language=language,
            provider=response.provider_name,
            model=response.model_used,
            prompt_version=prompt_version,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @staticmethod
    def _extract_json(content: str) -> Dict[str, Any]:
        """Safely extracts JSON blocks from markdown wrappers if the model ignores strict formatting rules."""
        if not content:
            return {}
            
        # Try direct parse first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Hunt for markdown JSON blocks, then fall back to the outermost object.
        patterns = [
            r"```(?:json)?\s*(\{.*?\})\s*```",
            r"(\{.*\})",
        ]
        for pattern in patterns:
            match = re.search(pattern, content, flags=re.DOTALL | re.IGNORECASE)
            if not match:
                continue
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.debug("Candidate JSON block could not be parsed.", exc_info=True)

        return {}
