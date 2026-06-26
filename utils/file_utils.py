# utils/file_utils.py
import os
from pathlib import Path

class FileUtils:
    """Utility methods for file system operations."""

    @staticmethod
    def safe_delete(file_path: Path) -> bool:
        """Deletes a file safely without raising exceptions if it doesn't exist."""
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
            return True
        except OSError:
            return False

    @staticmethod
    def get_file_size_mb(file_path: Path) -> float:
        """Returns the size of a file in Megabytes."""
        if not file_path.exists():
            return 0.0
        return os.path.getsize(file_path) / (1024 * 1024)