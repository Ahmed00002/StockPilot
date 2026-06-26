# gui/images/import_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget
from PySide6.QtCore import Qt

class ImportDialog(QDialog):
    """Allows users to select files or folders for bulk ingestion."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Images")
        self.setFixedSize(500, 400)
        self.setStyleSheet("QDialog { background-color: #252526; color: #cccccc; }")
        
        self.paths_to_import = []
        
        layout = QVBoxLayout(self)
        
        btn_layout = QHBoxLayout()
        self.btn_add_files = QPushButton("Add Files...")
        self.btn_add_files.clicked.connect(self._add_files)
        self.btn_add_folder = QPushButton("Add Folder...")
        self.btn_add_folder.clicked.connect(self._add_folder)
        
        btn_layout.addWidget(self.btn_add_files)
        btn_layout.addWidget(self.btn_add_folder)
        layout.addLayout(btn_layout)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #3e3e42; color: white;")
        layout.addWidget(self.list_widget)
        
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_import = QPushButton("Import")
        self.btn_import.clicked.connect(self.accept)
        self.btn_import.setStyleSheet("background-color: #007acc; color: white;")
        
        action_layout.addWidget(self.btn_cancel)
        action_layout.addWidget(self.btn_import)
        layout.addLayout(action_layout)

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.webp *.tiff)")
        if files:
            self.paths_to_import.extend(files)
            self.list_widget.addItems(files)

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.paths_to_import.append(folder)
            self.list_widget.addItem(f"[Folder] {folder}")
            
    def get_paths(self) -> list:
        return self.paths_to_import