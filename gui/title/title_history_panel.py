# gui/title/title_history_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from PySide6.QtCore import Signal
from typing import List, Dict, Any

class TitleHistoryPanel(QWidget):
    title_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Alternative Candidates")
        header.setStyleSheet("font-weight: bold;")
        
        self.history_list = QListWidget()
        self.history_list.setWordWrap(True)
        self.history_list.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(header)
        layout.addWidget(self.history_list)

    def update_history(self, alternatives: List[Dict[str, Any]]):
        self.history_list.clear()
        for alt in alternatives:
            item_text = f"{alt['title']}\nScore: {alt['score']}"
            item = QListWidgetItem(item_text)
            item.setData(100, alt['title']) 
            self.history_list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        title = item.data(100)
        self.title_selected.emit(title)