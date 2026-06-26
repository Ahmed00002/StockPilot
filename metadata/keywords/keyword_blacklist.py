# metadata/keywords/keyword_blacklist.py
from dataclasses import dataclass, field
from typing import Set

@dataclass
class KeywordBlacklist:
    banned_terms: Set[str] = field(default_factory=lambda: {
        "ai generated", "midjourney", "dall-e", "stable diffusion",
        "generative ai", "artificial intelligence generated",
        "prompt", "watermark", "copyright", "trademark",
        "vector image", "royalty free", "stock photo"
    })
    
    spam_terms: Set[str] = field(default_factory=lambda: {
        "best", "cheap", "download", "free", "sale", "discount",
        "high quality", "4k", "8k", "hd", "resolution"
    })

    def is_blacklisted(self, keyword: str) -> bool:
        lower_kw = keyword.lower()
        return lower_kw in self.banned_terms or lower_kw in self.spam_terms

DEFAULT_BLACKLIST = KeywordBlacklist()