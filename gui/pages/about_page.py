# gui/pages/about_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class AboutPage(QWidget):
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        layout = QVBoxLayout(self)
        lbl = QLabel("About StockPilot AI (Pending Implementation)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
