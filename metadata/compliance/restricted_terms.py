# metadata/compliance/restricted_terms.py
from dataclasses import dataclass, field
from typing import Set

@dataclass
class RestrictedTerms:
    banned_phrases: Set[str] = field(default_factory=lambda: {
        "ai generated", "midjourney", "dall-e", "stable diffusion",
        "generative ai", "artificial intelligence generated", "prompt"
    })
    
    spam_phrases: Set[str] = field(default_factory=lambda: {
        "click here", "buy now", "cheap", "free download",
        "best quality", "100%", "guaranteed", "watermark", "copyright"
    })

    def contains_restricted(self, text: str) -> bool:
        lower_text = text.lower()
        return any(term in lower_text for term in self.banned_phrases)
        
    def contains_spam(self, text: str) -> bool:
        lower_text = text.lower()
        return any(term in lower_text for term in self.spam_phrases)

DEFAULT_RESTRICTED_TERMS = RestrictedTerms()