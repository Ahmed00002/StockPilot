# image/filter_engine.py
from typing import List, Callable, Any
from image.image_model import ImageModel

class FilterEngine:
    """Provides querying capabilities over the ImageRepository."""

    @staticmethod
    def apply_filters(images: List[ImageModel], criteria: dict) -> List[ImageModel]:
        results = images
        
        if criteria.get("search"):
            q = criteria["search"].lower()
            results = [img for img in results if q in img.filename.lower() or any(q in t.lower() for t in img.tags)]
            
        if criteria.get("rating_min"):
            results = [img for img in results if img.rating >= criteria["rating_min"]]
            
        if criteria.get("is_favorite") is not None:
            results = [img for img in results if img.is_favorite == criteria["is_favorite"]]
            
        if criteria.get("color_label"):
            results = [img for img in results if img.color_label == criteria["color_label"]]
            
        if criteria.get("format"):
            results = [img for img in results if img.format == criteria["format"]]
            
        if criteria.get("collection_id"):
            results = [img for img in results if img.collection_id == criteria["collection_id"]]
            
        if criteria.get("status"):
            results = [img for img in results if img.status == criteria["status"]]

        return results