# metadata/workspace/revision_events.py
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict

class RevisionEventType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    MERGE = "merge"
    FAVORITE = "favorite"
    PIN = "pin"
    AUTOSAVE = "autosave"
    MANUAL_EDIT = "manual_edit"

@dataclass
class RevisionEvent:
    event_id: str
    image_hash: str
    event_type: RevisionEventType
    timestamp: str
    version_id: str
    details: Dict[str, Any]
    user: str = "system"