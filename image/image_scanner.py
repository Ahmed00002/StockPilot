# image/image_scanner.py
import logging
from pathlib import Path
from typing import List
from image.image_validator import ImageValidator

logger = logging.getLogger(__name__)

class ImageScanner:
    """Recursively scans directories to build file manifests before processing."""

    @staticmethod
    def scan_directory(directory: Path, recursive: bool = True) -> List[Path]:
        """Finds all potentially valid image files in a target directory."""
        found_files = []
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Invalid scan directory: {directory}")
            return found_files

        try:
            patterns = [f"*{ext}" for ext in ImageValidator.SUPPORTED_FORMATS]
            if recursive:
                for pattern in patterns:
                    found_files.extend(directory.rglob(pattern))
            else:
                for pattern in patterns:
                    found_files.extend(directory.glob(pattern))
                    
            # Filter out duplicates caused by case insensitivity and hidden files
            unique_files = {p.resolve() for p in found_files if not p.name.startswith('.')}
            logger.info(f"Scan discovered {len(unique_files)} potential assets.")
            return list(unique_files)
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            return []