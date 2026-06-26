# ai/prompt/template_version.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class TemplateVersion:
    """Tracks a specific historical revision of a PromptTemplate."""
    version_id: str
    template_id: str
    content: str
    version_tag: str
    created_at: datetime = field(default_factory=datetime.now)
    change_summary: Optional[str] = None
    author: str = "system"