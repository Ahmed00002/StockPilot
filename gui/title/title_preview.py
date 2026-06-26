# gui/title/title_preview.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

class TitlePreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Marketplace Preview")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        frame_layout = QVBoxLayout(self.preview_frame)
        
        self.title_display = QLabel("No title generated")
        self.title_display.setWordWrap(True)
        self.title_display.setStyleSheet("font-size: 16px; color: #333;")
        
        frame_layout.addWidget(self.title_display)
        layout.addWidget(self.preview_frame)
        layout.addStretch()

    def update_preview(self, title: str):
        if not title:
            self.title_display.setText("No title generated")
            self.title_display.setStyleSheet("font-size: 16px; color: #999;")
        else:
            self.title_display.setText(title)
            self.title_display.setStyleSheet("font-size: 16px; color: #000; font-weight: 500;")