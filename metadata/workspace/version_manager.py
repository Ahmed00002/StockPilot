# metadata/workspace/version_manager.py
import logging
from typing import List, Optional, Dict
from pathlib import Path

from metadata.workspace.metadata_snapshot import MetadataSnapshot
from metadata.workspace.version_storage import VersionStorage
from metadata.workspace.version_history import VersionHistory
from metadata.workspace.undo_manager import UndoManager
from metadata.workspace.favorite_manager import FavoriteManager
from metadata.workspace.timeline import WorkspaceTimeline, RevisionEventType
from metadata.workspace.revision_statistics import RevisionStatistics

logger = logging.getLogger(__name__)

class VersionManager:
    def __init__(self, workspace_dir: Path):
        self.storage = VersionStorage(workspace_dir)
        self.history = VersionHistory(self.storage)
        self.undo_mgr = UndoManager()
        self.favorites = FavoriteManager(workspace_dir)
        self.timeline = WorkspaceTimeline()
        self.statistics = RevisionStatistics(workspace_dir)

    def create_version(self, image_hash: str, title: str, description: str, keywords: List[str], provider: str, reason: str, scores: Dict[str, float] = None, current_active: MetadataSnapshot = None) -> MetadataSnapshot:
        if current_active:
            self.undo_mgr.push_state(image_hash, current_active)
            
        snapshot = self.history.create_version(image_hash, title, description, keywords, provider, reason, scores)
        
        self.timeline.add_event(image_hash, RevisionEventType.CREATE, snapshot.snapshot_id, {"reason": reason, "provider": provider})
        
        overall_score = scores.get("overall", 0.0) if scores else 0.0
        self.statistics.log_version(image_hash, snapshot.snapshot_id, provider, overall_score, is_merge=(reason=="merged"), is_manual=(reason=="manual"))
        
        return snapshot

    def get_all_versions(self, image_hash: str) -> List[MetadataSnapshot]:
        return self.history.get_history(image_hash)

    def get_version(self, image_hash: str, version_id: str) -> Optional[MetadataSnapshot]:
        return self.history.get_version(image_hash, version_id)

    def delete_version(self, image_hash: str, version_id: str) -> bool:
        success = self.history.delete_version(image_hash, version_id)
        if success:
            self.timeline.add_event(image_hash, RevisionEventType.DELETE, version_id, {})
        return success

    def restore_version(self, image_hash: str, version_id: str, current_active: MetadataSnapshot = None) -> Optional[MetadataSnapshot]:
        snapshot = self.get_version(image_hash, version_id)
        if not snapshot:
            return None
            
        if current_active:
            self.undo_mgr.push_state(image_hash, current_active)
            
        self.timeline.add_event(image_hash, RevisionEventType.RESTORE, version_id, {})
        return snapshot

    def undo(self, image_hash: str, current_active: MetadataSnapshot) -> Optional[MetadataSnapshot]:
        snapshot = self.undo_mgr.undo(image_hash, current_active)
        if snapshot:
            self.timeline.add_event(image_hash, RevisionEventType.RESTORE, snapshot.snapshot_id, {"action": "undo"})
        return snapshot

    def redo(self, image_hash: str, current_active: MetadataSnapshot) -> Optional[MetadataSnapshot]:
        snapshot = self.undo_mgr.redo(image_hash, current_active)
        if snapshot:
             self.timeline.add_event(image_hash, RevisionEventType.RESTORE, snapshot.snapshot_id, {"action": "redo"})
        return snapshot