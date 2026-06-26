# gui/pages/history_page.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class HistoryPage(QWidget):
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        layout = QVBoxLayout(self)
        lbl = QLabel("History (Pending Implementation)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
