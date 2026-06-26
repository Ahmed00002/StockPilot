# metadata/description/description_templates.py
from dataclasses import dataclass

@dataclass
class DescriptionPromptTemplate:
    system_prompt: str = (
        "You are an expert Commercial Stock Photography Copywriter. "
        "Your task is to generate highly natural, descriptive, and commercially viable stock descriptions. "
        "The description must seamlessly integrate the main subject, visual style, setting, and potential use cases. "
        "Do not use robotic keyword stuffing. Focus on readability and marketplace SEO. "
        "Do not include trademarks, brand names, or references to AI generation. "
        "Respond strictly with a JSON object containing a list of 'candidates', each with a 'description' string."
    )
    
    user_prompt_format: str = (
        "Subject: {subject}\n"
        "Scene/Setting: {scene}\n"
        "Objects present: {objects}\n"
        "Visual Style: {style}\n"
        "Concepts: {concepts}\n"
        "Keywords: {keywords}\n"
        "Generate 4 distinct, high-quality description candidates in natural sentence structure. "
        "Aim for 2 to 4 sentences."
    )

    def format_prompt(self, subject: str, scene: str, objects: str, style: str, concepts: str, keywords: str) -> str:
        return self.user_prompt_format.format(
            subject=subject,
            scene=scene,
            objects=objects,
            style=style,
            concepts=concepts,
            keywords=keywords
        )

STANDARD_DESCRIPTION_TEMPLATE = DescriptionPromptTemplate()