# gui/workspace/version_history_panel.py
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt

class VersionHistoryPanel(QWidget):
    version_selected = Signal(str)
    version_restored = Signal(str)
    version_deleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Version History")
        header.setStyleSheet("font-weight: bold;")
        layout.addWidget(header)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_restore = QPushButton("Restore")
        self.btn_restore.clicked.connect(self._on_restore)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self._on_delete)
        
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

    def update_history(self, versions: list, current_id: str = None):
        self.list_widget.clear()
        for v in versions:
            # INTEGRATION FIX: Import hoisted outside loop
            dt = datetime.fromisoformat(v.timestamp).strftime("%H:%M:%S")
            status = " (Active)" if v.snapshot_id == current_id else ""
            text = f"{dt} - {v.provider} [{v.reason}]{status}\nScore: {v.scores.get('overall', 0):.1f}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, v.snapshot_id)
            if v.snapshot_id == current_id:
                item.setBackground(Qt.GlobalColor.lightGray)
            self.list_widget.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        vid = item.data(Qt.ItemDataRole.UserRole)
        self.version_selected.emit(vid)

    def _on_restore(self):
        item = self.list_widget.currentItem()
        if item:
            self.version_restored.emit(item.data(Qt.ItemDataRole.UserRole))

    def _on_delete(self):
        item = self.list_widget.currentItem()
        if item:
            self.version_deleted.emit(item.data(Qt.ItemDataRole.UserRole))