# gui/images/image_filters.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QFrame
from PySide6.QtCore import Qt

class ImageFiltersPanel(QFrame):
    """Left-side panel allowing query modification over the Grid view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("""
            QFrame { background-color: #252526; border-right: 1px solid #3f3f46; color: #cccccc; }
            QLabel { font-weight: bold; margin-top: 10px; color: #ffffff; }
        """)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Status"))
        self.chk_pending = QCheckBox("Pending")
        self.chk_generated = QCheckBox("Generated")
        self.chk_exported = QCheckBox("Exported")
        layout.addWidget(self.chk_pending)
        layout.addWidget(self.chk_generated)
        layout.addWidget(self.chk_exported)
        
        layout.addWidget(QLabel("Ratings"))
        layout.addWidget(QCheckBox("5 Stars"))
        layout.addWidget(QCheckBox("Favorites Only"))
        
        layout.addStretch()