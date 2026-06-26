# metadata/workspace/favorite_manager.py
import json
import logging
from pathlib import Path
from typing import Set, Dict

logger = logging.getLogger(__name__)

class FavoriteManager:
    def __init__(self, workspace_dir: Path):
        self.favorites_file = workspace_dir / "favorites.json"
        self._favorites: Dict[str, Set[str]] = self._load_favorites()

    def _load_favorites(self) -> Dict[str, Set[str]]:
        if not self.favorites_file.exists():
            return {}
        try:
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {k: set(v) for k, v in data.items()}
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load favorites: {e}")
            return {}

    def _save_favorites(self) -> None:
        try:
            data = {k: list(v) for k, v in self._favorites.items()}
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save favorites: {e}")

    def toggle_favorite(self, image_hash: str, version_id: str) -> bool:
        if image_hash not in self._favorites:
            self._favorites[image_hash] = set()
            
        if version_id in self._favorites[image_hash]:
            self._favorites[image_hash].remove(version_id)
            is_fav = False
        else:
            self._favorites[image_hash].add(version_id)
            is_fav = True
            
        self._save_favorites()
        logger.debug(f"Toggled favorite for {version_id} -> {is_fav}")
        return is_fav

    def is_favorite(self, image_hash: str, version_id: str) -> bool:
        return version_id in self._favorites.get(image_hash, set())

    def get_favorites(self, image_hash: str) -> Set[str]:
        return self._favorites.get(image_hash, set())