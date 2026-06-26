# gui/workspaces/workspace_explorer.py
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QFileSystemModel, 
    QMenu, QMessageBox, QInputDialog, QLabel
)
from PySide6.QtCore import Qt, QDir, QModelIndex
from PySide6.QtGui import QAction, QCursor
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class WorkspaceExplorer(QWidget):
    """File system tree view displaying the active workspace project structure."""
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.current_workspace_path = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = QLabel("Project Explorer")
        self.header.setStyleSheet("background-color: #2d2d30; color: #cccccc; padding: 6px; font-weight: bold; border-bottom: 1px solid #3f3f46;")
        self.layout.addWidget(self.header)
        
        # File System Model
        self.model = QFileSystemModel()
        self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs | QDir.Filter.Files)
        
        # Tree View
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True) # Size
        self.tree.setColumnHidden(2, True) # Type
        self.tree.setColumnHidden(3, True) # Date
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                border: none;
                color: #cccccc;
            }
            QTreeView::item:hover { background-color: #2a2d2e; }
            QTreeView::item:selected { background-color: #37373d; }
        """)
        
        self.layout.addWidget(self.tree)
        self._subscribe_events()

    def _subscribe_events(self) -> None:
        if not self.container: return
        eb = self.container.get_service("event_bus")
        if eb:
            eb.subscribe(AppConstants.EVENT_WORKSPACE_LOADED, self.load_workspace)

    def load_workspace(self, workspace_name: str = None) -> None:
        if not self.container: return
        wm = self.container.get_service("workspace_manager")
        
        if wm and wm.active_workspace:
            self.current_workspace_path = wm.active_workspace.root_path
            root_idx = self.model.setRootPath(self.current_workspace_path)
            self.tree.setRootIndex(root_idx)
            self.header.setText(f"Project Explorer - {wm.active_workspace.name}")
        else:
            self.current_workspace_path = None
            self.tree.setRootIndex(QModelIndex())
            self.header.setText("Project Explorer")

    def _show_context_menu(self, position) -> None:
        if not self.current_workspace_path: return
        
        index = self.tree.indexAt(position)
        if not index.isValid(): return
        
        file_path = self.model.filePath(index)
        
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background-color: #252526; border: 1px solid #3f3f46; color: #cccccc; }
            QMenu::item:selected { background-color: #007acc; }
        """)
        
        act_expand = QAction("Expand All", self)
        act_expand.triggered.connect(lambda: self.tree.expandAll())
        
        act_collapse = QAction("Collapse All", self)
        act_collapse.triggered.connect(lambda: self.tree.collapseAll())
        
        act_rename = QAction("Rename...", self)
        act_rename.triggered.connect(lambda: self._rename_item(file_path, index))
        
        act_refresh = QAction("Refresh", self)
        act_refresh.triggered.connect(self._refresh_tree)
        
        menu.addAction(act_expand)
        menu.addAction(act_collapse)
        menu.addSeparator()
        menu.addAction(act_rename)
        menu.addSeparator()
        menu.addAction(act_refresh)
        
        menu.exec(self.tree.viewport().mapToGlobal(position))

    def _rename_item(self, old_path: str, index: QModelIndex) -> None:
        # INTEGRATION FIX: Prevent renaming of root workspace folder to avoid fatal state desync
        if Path(old_path).resolve() == Path(self.current_workspace_path).resolve():
            QMessageBox.warning(self, "Rename Denied", "You cannot rename the workspace root directory from the explorer.")
            return
            
        old_file = Path(old_path)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_file.name)
        if ok and new_name:
            new_path = old_file.parent / new_name
            try:
                old_file.rename(new_path)
                logger.info(f"Renamed {old_path} to {new_path}")
                
                # INTEGRATION FIX: Publish rename event so tracking managers can update references
                if self.container:
                    eb = self.container.get_service("event_bus")
                    if eb:
                        eb.publish("workspace_file_renamed", {"old_path": old_path, "new_path": str(new_path)})
                        
            except OSError as e:
                # INTEGRATION FIX: Handle OS locking and permission exceptions smoothly
                QMessageBox.warning(self, "Rename Failed", f"Could not rename item (it may be open or locked):\n{e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred:\n{e}")

    def _refresh_tree(self) -> None:
        if self.current_workspace_path:
            self.model.setRootPath("")
            self.model.setRootPath(self.current_workspace_path)