# image/image_indexer.py
import os
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable
from PySide6.QtGui import QImageReader
from image.image_model import ImageModel
from image.image_hash import ImageHasher
from image.image_validator import ImageValidator
from image.intelligence.image_intelligence_manager import ImageIntelligenceManager

logger = logging.getLogger(__name__)

class IndexerSignals(QObject):
    progress = Signal(int, int, str)
    completed = Signal(list)
    error = Signal(str)

class ImageIndexerTask(QRunnable):
    """Background worker that builds the ImageModel data structures safely."""

    def __init__(self, files: list[Path], workspace_id: str, workspace_root: Path, intelligence_manager: ImageIntelligenceManager):
        super().__init__()
        self.files = files
        self.workspace_id = workspace_id
        self.workspace_root = workspace_root
        self.intelligence = intelligence_manager
        self.signals = IndexerSignals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self) -> None:
        processed_models = []
        total = len(self.files)
        
        for index, file_path in enumerate(self.files):
            if self._is_cancelled:
                break
                
            self.signals.progress.emit(index, total, f"Indexing {file_path.name}...")
            
            is_valid, _ = ImageValidator.validate(file_path)
            if not is_valid:
                continue
                
            try:
                # Run Intelligence Analysis
                report = self.intelligence.analyze_image(file_path)
                
                reader = QImageReader(str(file_path))
                size = reader.size()
                
                stat = os.stat(file_path)
                
                try:
                    rel_path = str(file_path.relative_to(self.workspace_root))
                except ValueError:
                    # INTEGRATION FIX: Maintain pure relative portability by failing back 
                    # to local filename if absolute mapping fails across filesystem bounds.
                    rel_path = file_path.name
                
                model = ImageModel(
                    filename=file_path.name,
                    absolute_path=str(file_path),
                    relative_path=rel_path,
                    workspace_id=self.workspace_id,
                    file_size_bytes=stat.st_size,
                    width=size.width(),
                    height=size.height(),
                    aspect_ratio=size.width() / size.height() if size.height() > 0 else 0,
                    format=file_path.suffix.lstrip('.').upper(),
                    # INTEGRATION FIX: Corrected attribute calls to match ImageFingerprint dataclass
                    sha256_hash=report.fingerprint.sha256_hash,
                    perceptual_hash=report.fingerprint.perceptual_hash
                )
                processed_models.append(model)
                
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")

        if not self._is_cancelled:
            self.signals.completed.emit(processed_models)