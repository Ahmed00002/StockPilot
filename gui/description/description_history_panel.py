# gui/description/description_history_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from PySide6.QtCore import Signal, Qt
from typing import List, Dict, Any

class DescriptionHistoryPanel(QWidget):
    description_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Alternative Descriptions")
        header.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.history_list = QListWidget()
        self.history_list.setWordWrap(True)
        self.history_list.setSpacing(4)
        self.history_list.itemClicked.connect(self._on_item_clicked)
        
        layout.addWidget(header)
        layout.addWidget(self.history_list)

    def update_history(self, alternatives: List[Dict[str, Any]]):
        self.history_list.clear()
        for alt in alternatives:
            desc_preview = alt['description'][:80] + "..." if len(alt['description']) > 80 else alt['description']
            item_text = f"Score: {alt['score']}\n{desc_preview}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, alt['description'])
            self.history_list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        desc = item.data(Qt.ItemDataRole.UserRole)
        self.description_selected.emit(desc)