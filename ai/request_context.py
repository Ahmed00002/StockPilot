# ai/request_context.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

@dataclass
class RequestContext:
    """
    Contextual boundary object containing all necessary domain information 
    to process and execute an AI generation request.
    """
    prompt: str
    workspace: str
    language: str
    marketplace: str
    
    image_path: Optional[Path] = None
    
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30
    
    user_settings: Dict[str, Any] = field(default_factory=dict)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a user setting.
        
        Args:
            key: The configuration key to retrieve.
            default: The fallback value if the key does not exist.
            
        Returns:
            The setting value or the default.
        """
        return self.user_settings.get(key, default)