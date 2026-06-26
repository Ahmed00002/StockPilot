# image/image_validator.py
import logging
from pathlib import Path
from typing import Tuple, List
from PySide6.QtGui import QImageReader
from utils.file_utils import FileUtils

logger = logging.getLogger(__name__)

class ImageValidator:
    """Validates files against structural and format requirements."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".avif", ".heif"}

    @staticmethod
    def validate(file_path: Path) -> Tuple[bool, List[str]]:
        errors = []
        
        if not file_path.exists():
            errors.append("File does not exist.")
            return False, errors
            
        if file_path.suffix.lower() not in ImageValidator.SUPPORTED_FORMATS:
            errors.append(f"Unsupported format: {file_path.suffix}")
            return False, errors
            
        size_mb = FileUtils.get_file_size_mb(file_path)
        if size_mb == 0:
            errors.append("Zero-byte file.")
            
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except OSError:
            errors.append("Read permission denied.")

        if not errors:
            reader = QImageReader(str(file_path))
            if not reader.canRead():
                errors.append(f"Corrupted or unreadable image data: {reader.errorString()}")
            else:
                size = reader.size()
                if size.width() < 100 or size.height() < 100:
                    errors.append(f"Resolution too low ({size.width()}x{size.height()}).")

        if errors:
            logger.debug(f"Validation failed for {file_path.name}: {errors}")
            
        return len(errors) == 0, errors