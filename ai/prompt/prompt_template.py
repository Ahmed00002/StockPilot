# ai/prompt/prompt_template.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class PromptTemplate:
    """Represents an externalized, versionable prompt template definition."""
    id: str
    name: str
    description: str
    content: str
    target_marketplaces: List[str] = field(default_factory=list)
    required_variables: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict[str, str] = field(default_factory=dict)