# metadata/workspace/metadata_snapshot.py
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any

@dataclass
class MetadataSnapshot:
    snapshot_id: str
    image_hash: str
    title: str
    description: str
    keywords: List[str]
    provider: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reason: str = "auto"
    category: int = 0
    scores: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataSnapshot':
        return cls(**data)