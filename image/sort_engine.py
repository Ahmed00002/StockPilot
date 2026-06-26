# image/sort_engine.py
from typing import List
from image.image_model import ImageModel

class SortEngine:
    """Handles ordering of ImageModels for the grid view."""

    @staticmethod
    def sort(images: List[ImageModel], criteria: str, descending: bool = False) -> List[ImageModel]:
        key_func = None
        
        if criteria == "filename":
            key_func = lambda x: x.filename.lower()
        elif criteria == "date":
            key_func = lambda x: x.created_date
        elif criteria == "import_time":
            key_func = lambda x: x.imported_date
        elif criteria == "resolution":
            key_func = lambda x: x.resolution_megapixels
        elif criteria == "size":
            key_func = lambda x: x.file_size_bytes
        elif criteria == "rating":
            key_func = lambda x: x.rating
        else:
            key_func = lambda x: x.filename.lower() # Default fallback

        return sorted(images, key=key_func, reverse=descending)