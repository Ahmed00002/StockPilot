# image/image_statistics.py
from typing import List, Dict, Any
from image.image_model import ImageModel

class ImageStatistics:
    """Calculates dataset metrics for display in properties or dashboards."""

    @staticmethod
    def generate(images: List[ImageModel]) -> Dict[str, Any]:
        count = len(images)
        if count == 0:
            return {"total": 0, "size_mb": 0, "formats": {}}
            
        total_size = sum(img.file_size_bytes for img in images)
        formats = {}
        for img in images:
            formats[img.format] = formats.get(img.format, 0) + 1
            
        max_res = max(images, key=lambda x: x.resolution_megapixels).resolution_megapixels if images else 0
        
        return {
            "total": count,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "formats": formats,
            "max_megapixel": round(max_res, 1)
        }