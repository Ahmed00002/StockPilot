# metadata/workspace/version_storage.py
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil

from metadata.workspace.metadata_snapshot import MetadataSnapshot

logger = logging.getLogger(__name__)

class VersionStorage:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def _get_image_dir(self, image_hash: str) -> Path:
        image_dir = self.workspace_dir / image_hash
        image_dir.mkdir(exist_ok=True)
        return image_dir

    def save_version(self, snapshot: MetadataSnapshot) -> None:
        image_dir = self._get_image_dir(snapshot.image_hash)
        file_path = image_dir / f"{snapshot.snapshot_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f, indent=2)
            logger.debug(f"Saved version {snapshot.snapshot_id} for {snapshot.image_hash}")
        except IOError as e:
            logger.error(f"Failed to save version {snapshot.snapshot_id}: {e}")

    def load_version(self, image_hash: str, version_id: str) -> Optional[MetadataSnapshot]:
        file_path = self._get_image_dir(image_hash) / f"{version_id}.json"
        
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return MetadataSnapshot.from_dict(data)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load version {version_id}: {e}")
            return None

    def get_all_versions(self, image_hash: str) -> List[MetadataSnapshot]:
        image_dir = self._get_image_dir(image_hash)
        versions = []
        
        for file_path in image_dir.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    versions.append(MetadataSnapshot.from_dict(data))
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Error reading version file {file_path}: {e}")
                
        return sorted(versions, key=lambda x: x.timestamp, reverse=True)

    def delete_version(self, image_hash: str, version_id: str) -> bool:
        file_path = self._get_image_dir(image_hash) / f"{version_id}.json"
        if file_path.exists():
            try:
                file_path.unlink()
                logger.debug(f"Deleted version {version_id}")
                return True
            except OSError as e:
                logger.error(f"Failed to delete version {version_id}: {e}")
        return False

    def clear_workspace(self, image_hash: str) -> bool:
        image_dir = self._get_image_dir(image_hash)
        if image_dir.exists():
            try:
                shutil.rmtree(image_dir)
                logger.info(f"Cleared workspace for {image_hash}")
                return True
            except OSError as e:
                logger.error(f"Failed to clear workspace {image_hash}: {e}")
        return False