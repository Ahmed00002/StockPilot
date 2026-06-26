# metadata/keywords/keyword_generator.py
import json
import logging
from typing import List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class KeywordGenerationContext:
    subject: str
    scene: str
    objects: str
    style: str
    concepts: str
    marketplace: str
    language: str = "en"

class KeywordGenerator:
    def __init__(self, ai_manager: Any):
        self.ai_manager = ai_manager

    def generate_candidate_pool(self, context: KeywordGenerationContext, target_count: int = 70) -> List[str]:
        system_prompt = (
            "You are an expert Commercial Stock Photography SEO Specialist. "
            "Your task is to generate a comprehensive, highly commercial list of stock keywords based on the visual description. "
            "Include primary subjects, secondary elements, concepts, emotions, actions, colors, and industry terms. "
            "Include a mix of single words and highly relevant long-tail phrases (2-3 words). "
            f"Generate exactly {target_count} unique keywords. "
            "Respond strictly with a JSON object containing a flat list of strings under the key 'keywords'."
        )
        
        user_prompt = (
            f"Subject: {context.subject}\n"
            f"Scene: {context.scene}\n"
            f"Objects: {context.objects}\n"
            f"Style: {context.style}\n"
            f"Concepts: {context.concepts}\n"
            f"Marketplace target: {context.marketplace}\n"
            "Generate the keyword pool."
        )
        
        try:
            schema = {
                "type": "object", 
                "properties": {
                    "keywords": {
                        "type": "array", 
                        "items": {"type": "string"}
                    }
                }
            }
            response = self.ai_manager.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema
            )
            
            data = json.loads(response)
            keywords = data.get('keywords', [])
            
            logger.info(f"Generated {len(keywords)} candidate keywords.")
            return keywords

        except Exception as e:
            logger.error(f"Keyword generation failed: {e}")
            return []