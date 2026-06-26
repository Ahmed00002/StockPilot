# workspace/workspace_serializer.py
import json
import logging
from pathlib import Path
from typing import Optional
from workspace.workspace import Workspace, WorkspaceSettings, WorkspaceState

logger = logging.getLogger(__name__)

class WorkspaceSerializer:
    """Handles parsing and saving Workspace objects to JSON."""

    @staticmethod
    def save(workspace: Workspace) -> bool:
        config_path = workspace.paths.config_file
        workspace.touch()
        
        data = {
            "workspace_id": workspace.workspace_id,
            "name": workspace.name,
            "description": workspace.description,
            "author": workspace.author,
            "created_date": workspace.created_date,
            "modified_date": workspace.modified_date,
            "version": workspace.version,
            "root_path": str(workspace.root_path),
            "workspace_icon": workspace.workspace_icon,
            "marketplace_profile": workspace.marketplace_profile,
            "status": workspace.status,
            "tags": workspace.tags,
            "color_label": workspace.color_label,
            "is_pinned": workspace.is_pinned,
            "is_favorite": workspace.is_favorite,
            "settings": workspace.settings.__dict__,
            "state": workspace.state.__dict__
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except IOError as e:
            logger.error(f"Failed to save workspace config: {e}")
            return False

    @staticmethod
    def load(config_path: Path) -> Optional[Workspace]:
        if not config_path.exists():
            return None
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            settings = WorkspaceSettings(**data.get("settings", {}))
            state = WorkspaceState(**data.get("state", {}))
            
            # Remove nested objects before unpacking to avoid duplicate args
            data.pop("settings", None)
            data.pop("state", None)
            
            workspace = Workspace(**data)
            workspace.settings = settings
            workspace.state = state
            return workspace
        except Exception as e:
            logger.error(f"Failed to parse workspace config at {config_path}: {e}")
            return None