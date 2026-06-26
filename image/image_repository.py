# image/image_repository.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from image.image_model import ImageModel

logger = logging.getLogger(__name__)

class ImageRepository:
    """Manages the structured local JSON persistence of the entire workspace image index."""

    def __init__(self, workspace_root: Path):
        self.index_file = workspace_root / "metadata" / "_image_index.json"
        self._index: Dict[str, ImageModel] = {}
        self.load()

    def load(self) -> None:
        if not self.index_file.exists():
            self._index = {}
            return
            
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._index = {k: ImageModel(**v) for k, v in data.items()}
            logger.info(f"Loaded {len(self._index)} images from index.")
        except Exception as e:
            logger.error(f"Failed to load image index: {e}")
            self._index = {}

    def save(self) -> bool:
        try:
            data = {k: v.__dict__ for k, v in self._index.items()}
            # Atomic save mapping to prevent corruption
            temp_file = self.index_file.with_suffix(".tmp")
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            temp_file.replace(self.index_file)
            return True
        except Exception as e:
            logger.error(f"Failed to save image index: {e}")
            return False

    def add_or_update(self, image: ImageModel) -> None:
        self._index[image.image_id] = image
        
    def get(self, image_id: str) -> Optional[ImageModel]:
        return self._index.get(image_id)
        
    def get_all(self) -> List[ImageModel]:
        return list(self._index.values())
        
    def remove(self, image_id: str) -> bool:
        if image_id in self._index:
            del self._index[image_id]
            return True
        return False
        
    def exists_by_path(self, absolute_path: str) -> bool:
        return any(img.absolute_path == absolute_path for img in self._index.values())