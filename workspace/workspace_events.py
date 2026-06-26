# workspace/workspace_events.py
from dataclasses import dataclass
from workspace.workspace import Workspace

class WorkspaceEvents:
    """String constants for EventBus publishing."""
    CREATED = "workspace_created"
    LOADED = "workspace_loaded"
    CLOSED = "workspace_closed"
    SAVED = "workspace_saved"
    DELETED = "workspace_deleted"
    UPDATED = "workspace_updated"
    RECENT_UPDATED = "workspace_recent_updated"

@dataclass(frozen=True)
class WorkspaceEventPayload:
    workspace_id: str
    workspace_name: str
    path: str