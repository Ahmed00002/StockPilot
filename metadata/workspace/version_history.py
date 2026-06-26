# metadata/workspace/version_history.py
import logging
from typing import List, Dict, Optional
import uuid

from metadata.workspace.metadata_snapshot import MetadataSnapshot
from metadata.workspace.version_storage import VersionStorage

logger = logging.getLogger(__name__)

class VersionHistory:
    def __init__(self, storage: VersionStorage):
        self.storage = storage

    def create_version(self, image_hash: str, title: str, description: str, keywords: List[str], provider: str, reason: str = "auto", scores: Dict[str, float] = None) -> MetadataSnapshot:
        snapshot = MetadataSnapshot(
            snapshot_id=str(uuid.uuid4()),
            image_hash=image_hash,
            title=title,
            description=description,
            keywords=keywords,
            provider=provider,
            reason=reason,
            scores=scores or {}
        )
        self.storage.save_version(snapshot)
        logger.info(f"Created new metadata version: {snapshot.snapshot_id}")
        return snapshot

    def get_version(self, image_hash: str, version_id: str) -> Optional[MetadataSnapshot]:
        return self.storage.load_version(image_hash, version_id)

    def get_history(self, image_hash: str) -> List[MetadataSnapshot]:
        return self.storage.get_all_versions(image_hash)

    def duplicate_version(self, image_hash: str, version_id: str, new_reason: str = "duplicated") -> Optional[MetadataSnapshot]:
        original = self.get_version(image_hash, version_id)
        if not original:
            return None
            
        return self.create_version(
            image_hash=original.image_hash,
            title=original.title,
            description=original.description,
            keywords=original.keywords,
            provider=original.provider,
            reason=new_reason,
            scores=original.scores
        )

    def delete_version(self, image_hash: str, version_id: str) -> bool:
        return self.storage.delete_version(image_hash, version_id)