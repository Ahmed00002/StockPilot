# storage/workspace_storage.py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class WorkspaceRecentStorage:
    """Handles persistence of the recent workspaces list."""
    
    def __init__(self) -> None:
        self.storage_path = Path("config/recent_workspaces.json")
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not self.storage_path.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump([], f)

    def load_all(self) -> List[Dict[str, Any]]:
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load recent workspaces: {e}")
            return []

    def add_or_update(self, data: Dict[str, Any]) -> None:
        workspaces = self.load_all()
        # Remove existing if present to update
        workspaces = [w for w in workspaces if w.get("path") != data.get("path")]
        workspaces.append(data)
        self._save(workspaces)

    def remove(self, path: str) -> None:
        """Removes a workspace entry by path."""
        workspaces = self.load_all()
        filtered = [w for w in workspaces if w.get("path") != path]
        self._save(filtered)

    def _save(self, data: List[Dict[str, Any]]) -> None:
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save recent workspaces: {e}")