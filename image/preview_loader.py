# image/preview_loader.py
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable
from PySide6.QtGui import QImageReader, QImage, Qt

logger = logging.getLogger(__name__)

class PreviewSignals(QObject):
    loaded = Signal(str, QImage)
    error = Signal(str, str)

class PreviewLoaderTask(QRunnable):
    """Loads high-res images asynchronously to prevent UI freeze during preview."""

    def __init__(self, image_id: str, path: str):
        super().__init__()
        self.image_id = image_id
        self.path = path
        self.signals = PreviewSignals()

    def run(self) -> None:
        try:
            reader = QImageReader(self.path)
            reader.setAutoTransform(True)
            
            # Scale to max display bounds to save RAM (e.g., 4K max)
            size = reader.size()
            if size.isValid() and (size.width() > 3840 or size.height() > 2160):
                scaled = size.scaled(3840, 2160, Qt.AspectRatioMode.KeepAspectRatio)
                reader.setScaledSize(scaled)
                
            img = reader.read()
            if img.isNull():
                self.signals.error.emit(self.image_id, reader.errorString())
            else:
                self.signals.loaded.emit(self.image_id, img)
        except Exception as e:
            logger.error(f"Preview load failed: {e}")
            self.signals.error.emit(self.image_id, str(e))