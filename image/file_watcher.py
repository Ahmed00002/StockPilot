# image/file_watcher.py
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QFileSystemWatcher

logger = logging.getLogger(__name__)

class WorkspaceFileWatcher(QObject):
    """Monitors the local workspace directory for external modifications."""
    
    directory_changed = Signal(str)
    file_changed = Signal(str)

    def __init__(self, workspace_root: Path):
        super().__init__()
        self.watcher = QFileSystemWatcher(self)
        self.workspace_root = workspace_root
        
        target = self.workspace_root / "images"
        if target.exists():
            self.watcher.addPath(str(target))
            self.watcher.directoryChanged.connect(self.directory_changed.emit)
            self.watcher.fileChanged.connect(self.file_changed.emit)
            logger.debug(f"FileWatcher tracking: {target}")

    def update_paths(self) -> None:
        """Refreshes the watched paths based on current repository state."""
        # Future logic for adding subdirectories dynamically
        pass