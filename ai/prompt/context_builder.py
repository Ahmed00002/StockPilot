# ai/prompt/context_builder.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

@dataclass
class PromptContext:
    """Unified integration object carrying all systemic variables required during generation."""
    workspace_name: str
    language: str
    marketplace: str
    provider_name: str
    
    # Image Context
    filename: str = ""
    image_width: str = ""
    image_height: str = ""
    orientation: str = ""
    
    # Intelligence Context
    objects: str = ""
    scene: str = ""
    dominant_colors: str = ""
    copy_space: str = ""
    quality_score: str = ""
    
    # User Preferences
    user_style: str = ""
    
    # Computed Marketplace Limits
    keyword_limit: str = "50"
    title_limit: str = "200"
    description_limit: str = "200"
    
    def to_dict(self) -> Dict[str, str]:
        """Converts the active context boundary into a dictionary suitable for variable resolution."""
        return {
            "workspace": self.workspace_name,
            "language": self.language,
            "marketplace": self.marketplace,
            "provider": self.provider_name,
            "filename": self.filename,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "orientation": self.orientation,
            "objects": self.objects,
            "scene": self.scene,
            "dominant_colors": self.dominant_colors,
            "copy_space": self.copy_space,
            "quality_score": self.quality_score,
            "keyword_limit": self.keyword_limit,
            "title_limit": self.title_limit,
            "description_limit": self.description_limit,
            "user_style": self.user_style
        }

class ContextBuilder:
    """Assembles disjoint parameters from application state into a unified PromptContext object."""
    
    @staticmethod
    def build(
        workspace: str,
        language: str,
        marketplace: str,
        provider: str,
        image_path: Optional[Path] = None,
        intelligence_data: Optional[Dict[str, Any]] = None,
        user_prefs: Optional[Dict[str, str]] = None
    ) -> PromptContext:
        
        ctx = PromptContext(
            workspace_name=workspace,
            language=language,
            marketplace=marketplace,
            provider_name=provider
        )
        
        if image_path:
            ctx.filename = image_path.name
            
        if intelligence_data:
            ctx.image_width = str(intelligence_data.get("width", ""))
            ctx.image_height = str(intelligence_data.get("height", ""))
            ctx.orientation = intelligence_data.get("orientation", "")
            ctx.objects = intelligence_data.get("objects", "")
            ctx.scene = intelligence_data.get("scene", "")
            ctx.dominant_colors = intelligence_data.get("dominant_colors", "")
            ctx.copy_space = intelligence_data.get("copy_space", "")
            ctx.quality_score = str(intelligence_data.get("quality_score", ""))
            
        if user_prefs:
            ctx.user_style = user_prefs.get("user_style", "")

        from .marketplace_rules import MarketplaceRulesEngine
        rules = MarketplaceRulesEngine.get_rules(marketplace)
        if rules:
            ctx.keyword_limit = str(rules.keyword_max_count)
            ctx.title_limit = str(rules.title_max_length)
            ctx.description_limit = str(rules.description_max_length)
            
        return ctx