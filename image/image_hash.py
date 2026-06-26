# image/image_hash.py
import hashlib
import logging
from pathlib import Path
from PySide6.QtGui import QImage
from typing import Tuple

logger = logging.getLogger(__name__)

class ImageHasher:
    """Generates cryptographic and perceptual hashes for image files."""

    @staticmethod
    def generate_sha256(file_path: Path) -> str:
        """Calculates SHA-256 hash by reading in chunks to preserve RAM."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(65536), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except OSError as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""

    @staticmethod
    def generate_phash(file_path: Path) -> str:
        """Calculates a simple Average Hash (aHash) using QImage (safe off-main-thread)."""
        try:
            img = QImage(str(file_path))
            if img.isNull():
                return ""
            
            # Scale to 8x8 ignoring aspect ratio, and convert to grayscale
            scaled = img.scaled(8, 8)
            gray = scaled.convertToFormat(QImage.Format.Format_Grayscale8)
            
            pixels = []
            for y in range(8):
                for x in range(8):
                    pixels.append(gray.pixelColor(x, y).lightness())
                    
            avg = sum(pixels) / len(pixels)
            
            hash_bits = []
            for p in pixels:
                hash_bits.append('1' if p >= avg else '0')
                
            hash_int = int(''.join(hash_bits), 2)
            return f"{hash_int:016x}"
            
        except Exception as e:
            logger.error(f"Failed to generate pHash for {file_path}: {e}")
            return ""

    @staticmethod
    def generate_hashes(file_path: Path) -> Tuple[str, str]:
        """Returns (sha256, phash) for a given image."""
        return ImageHasher.generate_sha256(file_path), ImageHasher.generate_phash(file_path)