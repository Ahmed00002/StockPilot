# image/image_model.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import List, Optional

@dataclass
class ImageModel:
    """Domain model representing an indexed image asset."""
    filename: str
    absolute_path: str
    relative_path: str
    workspace_id: str
    
    image_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    file_size_bytes: int = 0
    width: int = 0
    height: int = 0
    aspect_ratio: float = 0.0
    orientation: str = "Landscape"
    format: str = "UNKNOWN"
    color_profile: str = "sRGB"
    
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_date: str = field(default_factory=lambda: datetime.now().isoformat())
    imported_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    thumbnail_path: Optional[str] = None
    sha256_hash: str = ""
    perceptual_hash: str = ""
    
    rating: int = 0
    color_label: str = "None"
    is_favorite: bool = False
    is_flagged: bool = False
    
    collection_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    status: str = "Pending"
    
    @property
    def resolution_megapixels(self) -> float:
        return (self.width * self.height) / 1_000_000.0