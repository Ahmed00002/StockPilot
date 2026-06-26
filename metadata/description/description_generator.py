# metadata/description/description_generator.py
import json
import logging
from typing import List, Any
from dataclasses import dataclass

from metadata.description.description_templates import STANDARD_DESCRIPTION_TEMPLATE

logger = logging.getLogger(__name__)

@dataclass
class DescriptionGenerationContext:
    subject: str
    scene: str
    objects: str
    style: str
    concepts: str
    keywords: str
    marketplace: str
    language: str = "en"

class DescriptionGenerator:
    def __init__(self, ai_manager: Any):
        self.ai_manager = ai_manager

    def generate_candidates(self, context: DescriptionGenerationContext, num_candidates: int = 4) -> List[str]:
        prompt = STANDARD_DESCRIPTION_TEMPLATE.format_prompt(
            subject=context.subject,
            scene=context.scene,
            objects=context.objects,
            style=context.style,
            concepts=context.concepts,
            keywords=context.keywords
        )
        
        system_instruction = STANDARD_DESCRIPTION_TEMPLATE.system_prompt
        
        try:
            response = self.ai_manager.generate_json(
                system_prompt=system_instruction,
                user_prompt=prompt,
                schema={
                    "type": "object", 
                    "properties": {
                        "candidates": {
                            "type": "array", 
                            "items": {
                                "type": "object", 
                                "properties": {"description": {"type": "string"}}
                            }
                        }
                    }
                }
            )
            
            data = json.loads(response)
            candidates = [c['description'] for c in data.get('candidates', [])][:num_candidates]
            
            if not candidates:
                logger.warning("AI returned no description candidates.")
            
            return candidates

        except Exception as e:
            logger.error(f"Description generation failed: {e}")
            return []