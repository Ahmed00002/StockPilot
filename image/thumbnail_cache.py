# image/thumbnail_cache.py
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtGui import QImage
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class ThumbnailCache:
    """Manages the disk persistence of optimized image thumbnails."""

    def __init__(self, workspace_thumb_dir: Path):
        self.thumb_dir = workspace_thumb_dir
        if not self.thumb_dir.exists():
            self.thumb_dir.mkdir(parents=True, exist_ok=True)

    def get_thumbnail_path(self, image_hash: str, size: int = 256) -> Path:
        """Determines the correct cache path based on content hash and size."""
        return self.thumb_dir / f"{image_hash}_{size}.jpg"

    def is_cached(self, image_hash: str, size: int = 256) -> bool:
        """Checks if a thumbnail already exists on disk."""
        return self.get_thumbnail_path(image_hash, size).exists()

    def save_thumbnail(self, image: QImage, image_hash: str, size: int = 256) -> Optional[str]:
        """Saves a processed QImage to the local thumbnail cache."""
        path = self.get_thumbnail_path(image_hash, size)
        try:
            if image.save(str(path), "JPG", 85):
                return str(path)
            return None
        except Exception as e:
            logger.error(f"Failed to save thumbnail {path.name}: {e}")
            return None