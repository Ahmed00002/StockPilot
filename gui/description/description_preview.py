# gui/description/description_preview.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class DescriptionPreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Marketplace Description Preview")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background-color: #fafafa; border: 1px solid #ddd; border-radius: 4px; padding: 12px;")
        frame_layout = QVBoxLayout(self.preview_frame)
        
        self.desc_display = QLabel("No description generated yet.")
        self.desc_display.setWordWrap(True)
        self.desc_display.setStyleSheet("font-size: 13px; color: #444; line-height: 1.5;")
        
        frame_layout.addWidget(self.desc_display)
        layout.addWidget(self.preview_frame)

    def update_preview(self, description: str):
        if not description.strip():
            self.desc_display.setText("No description generated yet.")
            self.desc_display.setStyleSheet("font-size: 13px; color: #999; font-style: italic;")
        else:
            self.desc_display.setText(description)
            self.desc_display.setStyleSheet("font-size: 13px; color: #333;")