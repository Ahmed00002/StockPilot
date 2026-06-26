# image/image_events.py
from dataclasses import dataclass
from typing import List

class ImageEvents:
    """String constants for Image-related EventBus publishing."""
    IMPORTED = "image_imported"
    INDEXED = "image_indexed"
    DELETED = "image_deleted"
    UPDATED = "image_updated"
    THUMBNAIL_READY = "thumbnail_ready"
    SELECTION_CHANGED = "image_selection_changed"
    SCAN_PROGRESS = "image_scan_progress"
    SCAN_COMPLETED = "image_scan_completed"

@dataclass(frozen=True)
class ImageEventPayload:
    workspace_id: str
    image_ids: List[str]

@dataclass(frozen=True)
class ScanProgressPayload:
    current: int
    total: int
    message: str