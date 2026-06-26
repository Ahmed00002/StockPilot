# gui/workspaces/workspace_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class BaseWorkspaceDialog(QDialog):
    """Base class for workspace creation and settings dialogs."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(600, 450)
        self.setStyleSheet("""
            QDialog { background-color: #252526; color: #cccccc; }
            QLabel { font-size: 13px; }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #3e3e42;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3e3e42;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
            }
            QPushButton:hover { background-color: #555555; }
            QPushButton#PrimaryAction { background-color: #007acc; }
            QPushButton#PrimaryAction:hover { background-color: #005f9e; }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout, 1)
        
        self.button_box = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_accept = QPushButton("Accept")
        self.btn_accept.setObjectName("PrimaryAction")
        # CRITICAL FIX: Wire the accept button so the dialog actually submits
        self.btn_accept.clicked.connect(self.accept) 
        
        self.button_box.addStretch()
        self.button_box.addWidget(self.btn_cancel)
        self.button_box.addWidget(self.btn_accept)
        
        self.main_layout.addLayout(self.button_box)