# workspace/workspace_backup.py
import logging
import zipfile
from datetime import datetime
from pathlib import Path
from workspace.workspace import Workspace

logger = logging.getLogger(__name__)

class WorkspaceBackupManager:
    """Creates ZIP archives of a workspace's configuration state."""

    @staticmethod
    def create_backup(workspace: Workspace) -> bool:
        paths = workspace.paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = paths.backups / f"workspace_backup_{timestamp}.zip"
        
        directories_to_backup = [
            paths.metadata,
            paths.prompts,
            paths.settings,
            paths.templates
        ]
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if paths.config_file.exists():
                    zipf.write(paths.config_file, paths.config_file.name)
                    
                for dir_path in directories_to_backup:
                    if dir_path.exists():
                        for file_path in dir_path.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(paths.root)
                                zipf.write(file_path, arcname)
            logger.info(f"Workspace backup created successfully: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create workspace backup: {e}")
            return False