# metadata/metadata_formatter.py
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("MetadataFormatter")

class MetadataFormatter:
    """Cleans, normalizes, and filters AI-generated metadata strings according to stock rules."""

    TRADEMARKS = [
        "nike", "apple", "iphone", "macbook", "coca-cola", "pepsi", "google", 
        "facebook", "instagram", "twitter", "tiktok", "disney", "marvel", 
        "star wars", "lego", "porsche", "ferrari", "rolex", "louis vuitton"
    ]

    BANNED_KEYWORD_TERMS = [
        "generative ai", "ai generated", "midjourney", "dall-e", "dalle", 
        "stable diffusion", "ai art", "artificial intelligence generated"
    ]

    @staticmethod
    def format_title(title: str, max_length: int = 200) -> str:
        if not title:
            return ""
        # Remove quotes, trailing periods, and excessive whitespace
        clean_title = re.sub(r'^["\']|["\']$', '', title.strip())
        clean_title = re.sub(r'\.$', '', clean_title)
        clean_title = " ".join(clean_title.split())
        
        # Remove trademarks
        for tm in MetadataFormatter.TRADEMARKS:
            pattern = re.compile(re.escape(tm), re.IGNORECASE)
            clean_title = pattern.sub("", clean_title)
            
        clean_title = " ".join(clean_title.split())
        return clean_title[:max_length]

    @staticmethod
    def format_description(description: str, max_length: int = 250) -> str:
        if not description:
            return ""
        clean_desc = re.sub(r'^["\']|["\']$', '', description.strip())
        clean_desc = " ".join(clean_desc.split())
        
        for tm in MetadataFormatter.TRADEMARKS:
            pattern = re.compile(re.escape(tm), re.IGNORECASE)
            clean_desc = pattern.sub("", clean_desc)
            
        clean_desc = " ".join(clean_desc.split())
        return clean_desc[:max_length]

    @staticmethod
    def format_keywords(keywords: List[str], max_count: int = 50) -> List[str]:
        if not keywords:
            return []
            
        clean_list = []
        seen = set()
        
        for kw in keywords:
            if not isinstance(kw, str):
                continue
                
            # Normalize
            k = kw.lower().strip()
            k = re.sub(r'[^\w\s-]', '', k) # Remove special chars except hyphens
            k = " ".join(k.split())
            
            if not k or len(k) < 2 or len(k) > 30:
                continue
                
            if k in seen:
                continue
                
            # Trademark & Banned Term filters
            is_banned = False
            for banned in MetadataFormatter.BANNED_KEYWORD_TERMS + MetadataFormatter.TRADEMARKS:
                if banned in k:
                    is_banned = True
                    break
                    
            if not is_banned:
                clean_list.append(k)
                seen.add(k)
                
            if len(clean_list) >= max_count:
                break
                
        return clean_list