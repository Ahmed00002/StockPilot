# storage/workspace_storage.py
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class WorkspaceRecentStorage:
    """Manages the global registry of known workspaces for quick access."""

    def __init__(self) -> None:
        self.registry_file = AppConstants.CONFIG_DIR / "recent_workspaces.json"
        if not self.registry_file.exists():
            self._save([])

    def _save(self, data: List[Dict[str, Any]]) -> None:
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save recent workspaces: {e}")

    def load_all(self) -> List[Dict[str, Any]]:
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read recent workspaces: {e}")
            return []

    def add_or_update(self, workspace_data: Dict[str, Any]) -> None:
        recents = self.load_all()
        # Remove if already exists to push to top
        recents = [w for w in recents if w.get("workspace_id") != workspace_data.get("workspace_id")]
        recents.insert(0, workspace_data)
        
        # Keep only last 20
        self._save(recents[:20])