# gui/workspaces/create_workspace_dialog.py
import re
from pathlib import Path
from PySide6.QtWidgets import QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QHBoxLayout, QFileDialog
from gui.workspaces.workspace_dialog import BaseWorkspaceDialog

class CreateWorkspaceDialog(BaseWorkspaceDialog):
    """Wizard dialog for generating a new workspace."""
    
    def __init__(self, parent=None):
        super().__init__("Create New Workspace", parent)
        self.btn_accept.setText("Create")
        self._build_form()

    def _build_form(self) -> None:
        self.content_layout.addWidget(QLabel("Workspace Name:"))
        self.inp_name = QLineEdit()
        self.content_layout.addWidget(self.inp_name)
        
        self.content_layout.addWidget(QLabel("Description:"))
        self.inp_desc = QTextEdit()
        self.inp_desc.setFixedHeight(60)
        self.content_layout.addWidget(self.inp_desc)
        
        loc_layout = QHBoxLayout()
        self.inp_path = QLineEdit()
        self.inp_path.setReadOnly(True)
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_path)
        loc_layout.addWidget(self.inp_path)
        loc_layout.addWidget(btn_browse)
        
        self.content_layout.addWidget(QLabel("Location (Base Directory):"))
        self.content_layout.addLayout(loc_layout)
        
        self.content_layout.addWidget(QLabel("Primary Marketplace:"))
        self.cmb_market = QComboBox()
        self.cmb_market.addItems(["Default", "Adobe Stock", "Shutterstock", "Freepik"])
        self.content_layout.addWidget(self.cmb_market)
        
        self.content_layout.addStretch()

    def _browse_path(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Base Directory for Workspace")
        if folder:
            self.inp_path.setText(folder)
            
    def get_data(self) -> dict:
        base_path = self.inp_path.text().strip()
        name = self.inp_name.text().strip()
        
        # INTEGRATION FIX: Sanitize name and append it to the base path 
        # to prevent overwriting the user's main root directories.
        safe_name = re.sub(r'[^\w\- ]', '', name).strip()
        
        final_path = ""
        if base_path and safe_name:
            final_path = str(Path(base_path) / safe_name)
            
        return {
            "name": name,
            "desc": self.inp_desc.toPlainText(),
            "path": final_path,
            "market": self.cmb_market.currentText()
        }