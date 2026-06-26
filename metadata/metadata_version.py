# metadata/metadata_version.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .metadata_models import GeneratedMetadata

@dataclass
class MetadataVersion:
    """Historical snapshot tracking mutations of metadata over time."""
    version_id: str
    metadata_id: str
    image_hash: str
    snapshot: GeneratedMetadata
    change_summary: str = "Initial generation"
    author: str = "system"
    is_favorite: bool = False
    is_archived: bool = False
    created_at: datetime = field(default_factory=datetime.now)