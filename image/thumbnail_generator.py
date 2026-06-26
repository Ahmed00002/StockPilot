# image/thumbnail_generator.py
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QRunnable, QObject, Signal, Qt
from PySide6.QtGui import QImageReader, QImage
from image.thumbnail_cache import ThumbnailCache

logger = logging.getLogger(__name__)

class ThumbnailGeneratorSignals(QObject):
    finished = Signal(str, str) # image_id, thumbnail_path
    error = Signal(str, str)    # image_id, error_message

class ThumbnailGeneratorTask(QRunnable):
    """Background task to scale down high-resolution images for grid views."""

    def __init__(self, image_id: str, original_path: Path, image_hash: str, target_size: int, cache: ThumbnailCache):
        super().__init__()
        self.image_id = image_id
        self.original_path = original_path
        self.image_hash = image_hash
        self.target_size = target_size
        self.cache = cache
        self.signals = ThumbnailGeneratorSignals()

    def run(self) -> None:
        try:
            if self.cache.is_cached(self.image_hash, self.target_size):
                path = self.cache.get_thumbnail_path(self.image_hash, self.target_size)
                self.signals.finished.emit(self.image_id, str(path))
                return

            reader = QImageReader(str(self.original_path))
            reader.setAutoTransform(True) # Apply EXIF orientation
            
            orig_size = reader.size()
            if orig_size.isValid():
                # Scale down reader bounds to prevent allocating full RAW to memory
                scaled_size = orig_size.scaled(self.target_size, self.target_size, Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(scaled_size)
                
            img = reader.read()
            if img.isNull():
                self.signals.error.emit(self.image_id, f"Failed to read image: {reader.errorString()}")
                return
                
            saved_path = self.cache.save_thumbnail(img, self.image_hash, self.target_size)
            if saved_path:
                self.signals.finished.emit(self.image_id, saved_path)
            else:
                self.signals.error.emit(self.image_id, "Failed to save thumbnail to cache.")
                
        except Exception as e:
            logger.error(f"Exception generating thumbnail for {self.original_path.name}: {e}")
            self.signals.error.emit(self.image_id, str(e))