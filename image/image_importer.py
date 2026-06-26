# image/image_importer.py
import shutil
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable
from utils.string_utils import StringUtils

logger = logging.getLogger(__name__)

class ImporterSignals(QObject):
    progress = Signal(int, int, str)
    completed = Signal(list)
    error = Signal(str)

class ImageImporterTask(QRunnable):
    """Copies external files safely into the Workspace images/ directory."""

    def __init__(self, source_files: list[Path], target_dir: Path):
        super().__init__()
        self.source_files = source_files
        self.target_dir = target_dir
        self.signals = ImporterSignals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self) -> None:
        imported_files = []
        total = len(self.source_files)
        
        for index, file_path in enumerate(self.source_files):
            if self._is_cancelled:
                break
                
            self.signals.progress.emit(index, total, f"Copying {file_path.name}...")
            
            try:
                safe_name = StringUtils.sanitize_filename(file_path.name)
                dest_path = self.target_dir / safe_name
                
                # Prevent overwrite
                counter = 1
                while dest_path.exists():
                    dest_path = self.target_dir / f"{dest_path.stem}_{counter}{dest_path.suffix}"
                    counter += 1
                    
                shutil.copy2(file_path, dest_path)
                imported_files.append(dest_path)
                
            except Exception as e:
                logger.error(f"Failed to import {file_path}: {e}")

        if not self._is_cancelled:
            self.signals.completed.emit(imported_files)