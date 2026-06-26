# metadata/title/title_generator.py
import json
import logging
from typing import List, Any
from dataclasses import dataclass

from metadata.title.title_templates import STANDARD_TEMPLATE

logger = logging.getLogger(__name__)

@dataclass
class GenerationContext:
    subject: str
    concepts: str
    keywords: str
    marketplace: str
    language: str = "en"

class TitleGenerator:
    def __init__(self, ai_manager: Any):
        self.ai_manager = ai_manager

    def generate_candidates(self, context: GenerationContext, num_candidates: int = 5) -> List[str]:
        prompt = STANDARD_TEMPLATE.format_prompt(
            subject=context.subject,
            concepts=context.concepts,
            keywords=context.keywords
        )
        
        system_instruction = STANDARD_TEMPLATE.system_prompt
        
        try:
            response = self.ai_manager.generate_json(
                system_prompt=system_instruction,
                user_prompt=prompt,
                schema={"type": "object", "properties": {"candidates": {"type": "array", "items": {"type": "object", "properties": {"title": {"type": "string"}}}}}}
            )
            
            data = json.loads(response)
            candidates = [c['title'] for c in data.get('candidates', [])][:num_candidates]
            
            if not candidates:
                logger.warning("AI returned no title candidates.")
            
            return candidates

        except Exception as e:
            logger.error(f"Title generation failed: {e}")
            return []