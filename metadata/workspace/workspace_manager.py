# metadata/workspace/workspace_manager.py
import logging
from typing import List, Optional, Dict
from pathlib import Path

from metadata.workspace.version_manager import VersionManager
from metadata.workspace.metadata_snapshot import MetadataSnapshot
from metadata.workspace.merge_engine import MergeEngine
from metadata.workspace.metadata_diff import MetadataDiffEngine, DiffResult
from metadata.metadata_formatter import MetadataFormatter

logger = logging.getLogger(__name__)

class MetadataWorkspaceManager:
    def __init__(self, base_dir: Path):
        self.workspace_dir = base_dir / "workspaces"
        self.version_mgr = VersionManager(self.workspace_dir)
        self.merge_engine = MergeEngine()
        self.diff_engine = MetadataDiffEngine()
        
        self.active_versions: Dict[str, MetadataSnapshot] = {}

    def init_workspace(self, image_hash: str) -> None:
        logger.info(f"Initialized workspace for {image_hash}")
        self.get_current(image_hash)
        
    def save_current(self, image_hash: str, title: str, description: str, keywords: List[str], provider: str, reason: str, scores: Dict[str, float] = None) -> MetadataSnapshot:
        # INTEGRATION FIX: Apply formatting rules before committing to version history
        clean_title = MetadataFormatter.format_title(title)
        clean_desc = MetadataFormatter.format_description(description)
        clean_kws = MetadataFormatter.format_keywords(keywords)

        current = self.active_versions.get(image_hash)
        snapshot = self.version_mgr.create_version(image_hash, clean_title, clean_desc, clean_kws, provider, reason, scores, current)
        self.active_versions[image_hash] = snapshot
        return snapshot

    def get_current(self, image_hash: str) -> Optional[MetadataSnapshot]:
        if image_hash in self.active_versions:
            return self.active_versions[image_hash]
            
        versions = self.version_mgr.get_all_versions(image_hash)
        if versions:
            self.active_versions[image_hash] = versions[0]
            return versions[0]
            
        return None

    def load_version(self, image_hash: str, version_id: str) -> Optional[MetadataSnapshot]:
        current = self.active_versions.get(image_hash)
        snapshot = self.version_mgr.restore_version(image_hash, version_id, current)
        if snapshot:
            self.active_versions[image_hash] = snapshot
        return snapshot

    def perform_merge(self, image_hash: str, base_id: str, other_id: str, config: Dict[str, str]) -> Optional[MetadataSnapshot]:
        base = self.version_mgr.get_version(image_hash, base_id)
        other = self.version_mgr.get_version(image_hash, other_id)
        
        if not base or not other:
            logger.error("Merge failed: version not found.")
            return None
            
        merged = self.merge_engine.merge_versions(
            base=base,
            other=other,
            use_title_from=config.get('title', 'base'),
            use_desc_from=config.get('description', 'base'),
            kw_merge_strategy=config.get('keywords', 'union')
        )
        
        # INTEGRATION FIX: Apply formatting to merged combinations before saving
        clean_title = MetadataFormatter.format_title(merged.title)
        clean_desc = MetadataFormatter.format_description(merged.description)
        clean_kws = MetadataFormatter.format_keywords(merged.keywords)
        
        current = self.active_versions.get(image_hash)
        snapshot = self.version_mgr.create_version(
            image_hash=image_hash,
            title=clean_title,
            description=clean_desc,
            keywords=clean_kws,
            provider=merged.provider,
            reason="merged",
            current_active=current
        )
        
        self.active_versions[image_hash] = snapshot
        return snapshot

    def compare_versions(self, image_hash: str, v1_id: str, v2_id: str) -> Optional[DiffResult]:
        v1 = self.version_mgr.get_version(image_hash, v1_id)
        v2 = self.version_mgr.get_version(image_hash, v2_id)
        if not v1 or not v2:
            return None
        return self.diff_engine.compare(v1, v2)