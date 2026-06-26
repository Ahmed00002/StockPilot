# workspace/workspace_loader.py
import logging
from pathlib import Path
from typing import Optional
from workspace.workspace import Workspace
from workspace.workspace_validator import WorkspaceValidator
from workspace.workspace_serializer import WorkspaceSerializer
from core.event_bus import EventBus
from workspace.workspace_events import WorkspaceEvents, WorkspaceEventPayload

logger = logging.getLogger(__name__)

class WorkspaceLoader:
    """Handles the transactional opening and validation of a Workspace."""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def open_workspace(self, root_path: str) -> Optional[Workspace]:
        path = Path(root_path)
        is_valid, errors = WorkspaceValidator.validate(path)
        
        if not is_valid:
            logger.error(f"Failed to load workspace at {root_path}. Validation errors: {errors}")
            return None
        
        config_path = path / "workspace.json"
        workspace = WorkspaceSerializer.load(config_path)
        
        if workspace:
            payload = WorkspaceEventPayload(workspace.workspace_id, workspace.name, workspace.root_path)
            self.event_bus.publish(WorkspaceEvents.LOADED, payload)
            logger.info(f"Successfully loaded workspace: {workspace.name}")
        return workspace