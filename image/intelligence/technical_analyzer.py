# image/intelligence/technical_analyzer.py
from PIL import Image
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class TechnicalData:
    width: int
    height: int
    aspect_ratio: float
    resolution: tuple[int, int]
    megapixels: float
    color_space: str
    bit_depth: int
    dpi: tuple[int, int]
    file_signature: str
    file_size_bytes: int

class TechnicalAnalyzer:
    MAGIC_NUMBERS = {
        b'\xff\xd8\xff': 'JPEG',
        b'\x89PNG\r\n\x1a\n': 'PNG',
        b'II*\x00': 'TIFF',
        b'MM\x00*': 'TIFF',
        b'WEBP': 'WEBP'
    }

    @staticmethod
    def get_file_signature(file_path: Path) -> str:
        with open(file_path, 'rb') as f:
            header = f.read(12)
            for magic, sig in TechnicalAnalyzer.MAGIC_NUMBERS.items():
                if header.startswith(magic) or magic in header:
                    return sig
        return "UNKNOWN"

    @staticmethod
    def analyze(file_path: Path) -> TechnicalData:
        file_size = os.path.getsize(file_path)
        signature = TechnicalAnalyzer.get_file_signature(file_path)
        
        with Image.open(file_path) as img:
            width, height = img.size
            aspect_ratio = round(width / height, 4) if height > 0 else 0.0
            megapixels = round((width * height) / 1_000_000, 2)
            color_space = img.mode
            
            bit_depth = 8
            if hasattr(img, 'bits'):
                bit_depth = img.bits
            elif img.mode == 'I;16':
                bit_depth = 16
                
            dpi = img.info.get('dpi', (72, 72))
            if isinstance(dpi, int):
                dpi = (dpi, dpi)
                
            return TechnicalData(
                width=width,
                height=height,
                aspect_ratio=aspect_ratio,
                resolution=(width, height),
                megapixels=megapixels,
                color_space=color_space,
                bit_depth=bit_depth,
                dpi=tuple(map(int, dpi)),
                file_signature=signature,
                file_size_bytes=file_size
            )