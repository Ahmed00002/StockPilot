# metadata/workspace/merge_engine.py
import logging
from typing import List, Set, Dict

from metadata.workspace.metadata_snapshot import MetadataSnapshot

logger = logging.getLogger(__name__)

class MergeEngine:
    def __init__(self):
        pass

    def merge_versions(self, base: MetadataSnapshot, other: MetadataSnapshot, use_title_from: str, use_desc_from: str, kw_merge_strategy: str) -> MetadataSnapshot:
        logger.info(f"Merging {base.snapshot_id} and {other.snapshot_id}")
        
        new_title = base.title if use_title_from == 'base' else other.title
        new_desc = base.description if use_desc_from == 'base' else other.description
        
        merged_kws: List[str] = []
        if kw_merge_strategy == 'base':
            merged_kws = list(base.keywords)
        elif kw_merge_strategy == 'other':
            merged_kws = list(other.keywords)
        elif kw_merge_strategy == 'union':
            seen = set()
            merged_kws = []
            for kw in base.keywords + other.keywords:
                kw_lower = kw.lower()
                if kw_lower not in seen:
                    seen.add(kw_lower)
                    merged_kws.append(kw)
        elif kw_merge_strategy == 'intersect':
            base_set = set(k.lower() for k in base.keywords)
            merged_kws = [k for k in other.keywords if k.lower() in base_set]
            
        provider = f"merged({base.provider},{other.provider})"
        
        import uuid
        merged_snapshot = MetadataSnapshot(
            snapshot_id=str(uuid.uuid4()),
            image_hash=base.image_hash,
            title=new_title,
            description=new_desc,
            keywords=merged_kws,
            provider=provider,
            reason="merged"
        )
        
        return merged_snapshot