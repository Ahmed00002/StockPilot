# metadata/workspace/timeline.py
import logging
from typing import List, Dict
from datetime import datetime
import uuid

from metadata.workspace.revision_events import RevisionEvent, RevisionEventType

logger = logging.getLogger(__name__)

class WorkspaceTimeline:
    def __init__(self):
        self._events: Dict[str, List[RevisionEvent]] = {}

    def add_event(self, image_hash: str, event_type: RevisionEventType, version_id: str, details: dict, user: str = "system"):
        if image_hash not in self._events:
            self._events[image_hash] = []
            
        event = RevisionEvent(
            event_id=str(uuid.uuid4()),
            image_hash=image_hash,
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat(),
            version_id=version_id,
            details=details,
            user=user
        )
        self._events[image_hash].append(event)
        logger.debug(f"Timeline event added for {image_hash}: {event_type.value}")

    def get_timeline(self, image_hash: str) -> List[RevisionEvent]:
        events = self._events.get(image_hash, [])
        return sorted(events, key=lambda x: x.timestamp, reverse=True)

    def clear(self, image_hash: str):
        if image_hash in self._events:
            del self._events[image_hash]