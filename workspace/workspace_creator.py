# workspace/workspace_creator.py
import logging
from pathlib import Path
from workspace.workspace import Workspace
from workspace.workspace_paths import WorkspacePaths

logger = logging.getLogger(__name__)

class WorkspaceCreator:
    """Handles the physical generation of new workspaces on disk."""

    @staticmethod
    def create_structural_foundation(workspace: Workspace) -> bool:
        paths = workspace.paths
        
        try:
            if not paths.root.exists():
                paths.root.mkdir(parents=True, exist_ok=True)
                
            for directory in paths.get_all_directories():
                directory.mkdir(exist_ok=True)
                
            # Initialize empty structural files if needed
            (paths.settings / "export_profiles.json").write_text("[]")
            (paths.settings / "keyword_presets.json").write_text("[]")
            
            logger.info(f"Workspace directories created at {paths.root}")
            return True
        except OSError as e:
            logger.error(f"Failed to create workspace structures: {e}")
            return False