# metadata/title/title_templates.py
from dataclasses import dataclass

@dataclass
class TitlePromptTemplate:
    system_prompt: str = (
        "You are a professional Commercial Stock Photography SEO Expert. "
        "Your task is to generate highly commercial, marketplace-safe titles for stock images based on the provided metadata and visual descriptions. "
        "The title must be natural English, descriptive, and highly searchable. "
        "Avoid keyword stuffing, clickbait, trademarked names, or mentioning AI generation. "
        "Respond strictly with a JSON object containing a list of 'candidates', each with a 'title' string."
    )
    
    user_prompt_format: str = (
        "Image Subject: {subject}\n"
        "Visual Concepts: {concepts}\n"
        "Keywords: {keywords}\n"
        "Generate 5 distinct, high-quality title candidates for this asset."
    )

    def format_prompt(self, subject: str, concepts: str, keywords: str) -> str:
        return self.user_prompt_format.format(
            subject=subject,
            concepts=concepts,
            keywords=keywords
        )

STANDARD_TEMPLATE = TitlePromptTemplate()