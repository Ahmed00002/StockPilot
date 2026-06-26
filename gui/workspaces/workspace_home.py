# gui/workspaces/workspace_home.py
"""Workspace home page for managing and creating workspaces."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFrame, QFileDialog, QMessageBox,
    QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class WorkspaceHomePage(QWidget):
    """Main workspace management page showing recent workspaces and creation options."""
    
    action_requested = Signal(str, dict)
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self._setup_ui()
        self._load_recent_workspaces()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Workspaces")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #ffffff; padding: 10px;")
        layout.addWidget(header)
        
        # Create workspace button
        self.btn_new_workspace = QPushButton("+ New Workspace")
        self.btn_new_workspace.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.btn_new_workspace.clicked.connect(self._create_new_workspace)
        layout.addWidget(self.btn_new_workspace)
        
        # Recent workspaces section
        recent_label = QLabel("Recent Workspaces")
        recent_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        recent_label.setStyleSheet("color: #cccccc; padding: 10px 0;")
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                color: #cccccc;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3f3f46;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.recent_list.itemDoubleClicked.connect(self._open_selected_workspace)
        layout.addWidget(self.recent_list)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("📁 Open Workspace...")
        self.btn_open.clicked.connect(self._open_workspace_dialog)
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #3f3f46;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        
        self.btn_remove = QPushButton("Remove from List")
        self.btn_remove.clicked.connect(self._remove_selected)
        self.btn_remove.setStyleSheet("""
            QPushButton {
                background-color: #3f3f46;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4f4f56;
            }
        """)
        
        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
    
    def _load_recent_workspaces(self):
        """Load recent workspaces from the workspace manager."""
        self.recent_list.clear()
        
        if not self.container:
            return
            
        wm = self.container.get_service("workspace_manager")
        if not wm:
            return
            
        recent = wm.get_recent_workspaces()
        for ws in recent:
            name = ws.get("name", "Unknown")
            path = ws.get("path", "")
            marketplace = ws.get("marketplace", "Default")
            item_text = f"{name} ({marketplace})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, path)
            item.setToolTip(f"Path: {path}\nMarketplace: {marketplace}")
            self.recent_list.addItem(item)
    
    def _create_new_workspace(self):
        """Open dialog to create a new workspace."""
        dialog = CreateWorkspaceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_workspace_data()
            if self.container:
                wm = self.container.get_service("workspace_manager")
                if wm:
                    ws = wm.create_workspace(
                        name=data["name"],
                        root_path=data["path"],
                        author=data.get("author", ""),
                        desc=data.get("description", ""),
                        marketplace=data.get("marketplace", "Default")
                    )
                    if ws:
                        QMessageBox.information(self, "Success", f"Workspace '{ws.name}' created successfully!")
                        self._load_recent_workspaces()
                        self.action_requested.emit("images", {})
                    else:
                        QMessageBox.critical(self, "Error", "Failed to create workspace. Check logs for details.")
    
    def _open_selected_workspace(self, item: QListWidgetItem):
        """Open the selected workspace from the list."""
        path = item.data(Qt.UserRole)
        if path and self.container:
            wm = self.container.get_service("workspace_manager")
            if wm:
                if wm.load_workspace(path):
                    self.action_requested.emit("images", {})
                else:
                    QMessageBox.critical(self, "Error", f"Failed to load workspace at {path}")
    
    def _open_workspace_dialog(self):
        """Open file dialog to select a workspace directory."""
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace Directory")
        if folder and self.container:
            wm = self.container.get_service("workspace_manager")
            if wm:
                if wm.load_workspace(folder):
                    self.action_requested.emit("images", {})
                else:
                    QMessageBox.critical(self, "Error", f"Failed to load workspace at {folder}")
    
    def _remove_selected(self):
        """Remove selected workspace from recent list."""
        current_item = self.recent_list.currentItem()
        if current_item and self.container:
            path = current_item.data(Qt.UserRole)
            wm = self.container.get_service("workspace_manager")
            if wm:
                wm.remove_recent(path)
                self._load_recent_workspaces()


class CreateWorkspaceDialog(QDialog):
    """Dialog for creating a new workspace."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Workspace")
        self.setMinimumWidth(500)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("My Stock Collection")
        form_layout.addRow("Name:", self.txt_name)
        
        # Location
        location_layout = QHBoxLayout()
        self.txt_location = QLineEdit()
        self.txt_location.setPlaceholderText("Select workspace location...")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self._browse_location)
        location_layout.addWidget(self.txt_location)
        location_layout.addWidget(self.btn_browse)
        form_layout.addRow("Location:", location_layout)
        
        # Author
        self.txt_author = QLineEdit()
        self.txt_author.setPlaceholderText("Your name or studio")
        form_layout.addRow("Author:", self.txt_author)
        
        # Description
        self.txt_description = QLineEdit()
        self.txt_description.setPlaceholderText("Optional description")
        form_layout.addRow("Description:", self.txt_description)
        
        # Marketplace
        self.combo_marketplace = QComboBox()
        self.combo_marketplace.addItems(["Default", "Adobe Stock", "Shutterstock", "Getty Images", "iStock"])
        form_layout.addRow("Target Marketplace:", self.combo_marketplace)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_location(self):
        """Open folder browser for workspace location."""
        folder = QFileDialog.getExistingDirectory(self, "Select Workspace Location")
        if folder:
            self.txt_location.setText(folder)
    
    def get_workspace_data(self):
        """Get the workspace data from the dialog."""
        return {
            "name": self.txt_name.text().strip(),
            "path": self.txt_location.text().strip(),
            "author": self.txt_author.text().strip(),
            "description": self.txt_description.text().strip(),
            "marketplace": self.combo_marketplace.currentText()
        }
