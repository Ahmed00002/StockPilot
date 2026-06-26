# workspace/workspace_manager.py
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from workspace.workspace import Workspace
from workspace.workspace_creator import WorkspaceCreator
from workspace.workspace_serializer import WorkspaceSerializer
from workspace.workspace_loader import WorkspaceLoader
from workspace.workspace_backup import WorkspaceBackupManager
from workspace.workspace_validator import WorkspaceValidator
from storage.workspace_storage import WorkspaceRecentStorage
from core.event_bus import EventBus
from core.constants import AppConstants
from workspace.workspace_events import WorkspaceEvents, WorkspaceEventPayload

logger = logging.getLogger(__name__)

class WorkspaceManager:
    """Singleton service orchestrating all Workspace operations and state."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus
        self.loader = WorkspaceLoader(event_bus)
        self.recent_storage = WorkspaceRecentStorage()
        self.active_workspace: Optional[Workspace] = None

    def create_workspace(self, name: str, root_path: str, author: str = "", desc: str = "", marketplace: str = "Default") -> Optional[Workspace]:
        ws = Workspace(name=name, root_path=root_path, author=author, description=desc)
        
        # INTEGRATION FIX: Assigning the correct marketplace parameters dynamically
        ws.settings.marketplace = marketplace
        ws.marketplace_profile = marketplace
        
        if WorkspaceCreator.create_structural_foundation(ws):
            if WorkspaceSerializer.save(ws):
                self._update_recent(ws)
                self.active_workspace = ws
                payload = WorkspaceEventPayload(ws.workspace_id, ws.name, ws.root_path)
                self.event_bus.publish(WorkspaceEvents.CREATED, payload)
                self.event_bus.publish(AppConstants.EVENT_WORKSPACE_LOADED, ws.name)
                return ws
        return None

    def load_workspace(self, root_path: str) -> bool:
        # INTEGRATION FIX: Validate workspace integrity before attempting to parse it
        path_obj = Path(root_path)
        if path_obj.exists():
            is_valid, errors = WorkspaceValidator.validate(path_obj)
            if not is_valid:
                logger.error(f"Workspace validation failed for '{root_path}': {errors}")
                return False
                
        if self.active_workspace:
            self.close_workspace()
            
        ws = self.loader.open_workspace(root_path)
        if ws:
            self.active_workspace = ws
            self._update_recent(ws)
            self.event_bus.publish(AppConstants.EVENT_WORKSPACE_LOADED, ws.name)
            
            try:
                payload = WorkspaceEventPayload(ws.workspace_id, ws.name, ws.root_path)
                if hasattr(WorkspaceEvents, 'LOADED'):
                    self.event_bus.publish(WorkspaceEvents.LOADED, payload)
            except Exception as e:
                logger.debug(f"Failed to publish secondary event: {e}")
                
            return True
        return False

    def save_workspace(self) -> bool:
        if not self.active_workspace:
            return False
            
        if WorkspaceSerializer.save(self.active_workspace):
            payload = WorkspaceEventPayload(self.active_workspace.workspace_id, self.active_workspace.name, self.active_workspace.root_path)
            self.event_bus.publish(WorkspaceEvents.SAVED, payload)
            return True
        return False

    def close_workspace(self) -> None:
        if self.active_workspace:
            if self.active_workspace.settings.auto_backup:
                WorkspaceBackupManager.create_backup(self.active_workspace)
            self.save_workspace()
            payload = WorkspaceEventPayload(self.active_workspace.workspace_id, self.active_workspace.name, self.active_workspace.root_path)
            self.event_bus.publish(WorkspaceEvents.CLOSED, payload)
            self.event_bus.publish(AppConstants.EVENT_WORKSPACE_LOADED, None)
            self.active_workspace = None

    def remove_recent(self, path: str) -> None:
        """Prunes a workspace from recent storage."""
        self.recent_storage.remove(path)
        self.event_bus.publish(WorkspaceEvents.RECENT_UPDATED)

    def get_recent_workspaces(self) -> List[Dict[str, Any]]:
        return self.recent_storage.load_all()

    def _update_recent(self, ws: Workspace) -> None:
        data = {
            "workspace_id": ws.workspace_id,
            "name": ws.name,
            "path": ws.root_path,
            "marketplace": ws.marketplace_profile,
            "is_pinned": ws.is_pinned,
            "is_favorite": ws.is_favorite,
            "last_opened": ws.modified_date
        }
        self.recent_storage.add_or_update(data)
        self.event_bus.publish(WorkspaceEvents.RECENT_UPDATED)