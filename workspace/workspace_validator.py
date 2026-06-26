# workspace/workspace_validator.py
import logging
from pathlib import Path
from typing import Tuple, List
from workspace.workspace_paths import WorkspacePaths

logger = logging.getLogger(__name__)

class WorkspaceValidator:
    """Analyzes a directory to ensure structural and permission integrity."""

    @staticmethod
    def validate(workspace_path: Path) -> Tuple[bool, List[str]]:
        errors = []
        paths = WorkspacePaths(workspace_path)
        
        if not workspace_path.exists():
            errors.append(f"ERR_ROOT_NOT_EXIST: Workspace root directory '{workspace_path}' does not exist.")
            return False, errors
            
        if not paths.config_file.exists():
            errors.append("ERR_MISSING_CONFIG: Missing workspace.json configuration file.")
            
        try:
            test_file = workspace_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except OSError:
            errors.append("ERR_PERMISSION_DENIED: Cannot write to workspace directory.")

        for directory in paths.get_all_directories():
            if not directory.exists():
                errors.append(f"ERR_MISSING_DIR: Missing required directory: {directory.name}/")
                
        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Workspace validation failed for {workspace_path}: {errors}")
            
        return is_valid, errors

    @staticmethod
    def generate_repair_plan(errors: List[str]) -> List[str]:
        suggestions = []
        for error in errors:
            if "ERR_MISSING_DIR" in error:
                suggestions.append("Recreate missing subdirectories.")
            elif "ERR_PERMISSION_DENIED" in error:
                suggestions.append("Run application as Administrator or change folder permissions.")
            elif "ERR_MISSING_CONFIG" in error:
                suggestions.append("Restore configuration from the backups/ folder.")
        return suggestions