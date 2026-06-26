# image/collection_manager.py
from typing import Dict, List, Optional
import uuid

class CollectionManager:
    """Manages virtual groupings of images without moving files on disk."""
    
    def __init__(self):
        # Maps Collection ID -> Name
        self.collections: Dict[str, str] = {}
        
    def create_collection(self, name: str) -> str:
        coll_id = str(uuid.uuid4())
        self.collections[coll_id] = name
        return coll_id
        
    def rename_collection(self, coll_id: str, new_name: str) -> bool:
        if coll_id in self.collections:
            self.collections[coll_id] = new_name
            return True
        return False
        
    def delete_collection(self, coll_id: str) -> bool:
        if coll_id in self.collections:
            del self.collections[coll_id]
            return True
        return False
        
    def get_collections(self) -> Dict[str, str]:
        return self.collections.copy()