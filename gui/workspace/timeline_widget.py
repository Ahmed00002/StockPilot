# gui/workspace/timeline_widget.py
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QListWidgetItem
from PySide6.QtCore import Qt

class TimelineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Workspace Timeline")
        header.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(header)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("QListWidget::item { padding: 4px; border-bottom: 1px solid #f0f0f0; }")
        layout.addWidget(self.list_widget)

    def update_timeline(self, events: list):
        self.list_widget.clear()
        if not events:
            self.list_widget.addItem("No events recorded.")
            return
            
        for event in events:
            # INTEGRATION FIX: Import hoisted outside loop
            dt = datetime.fromisoformat(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            ev_type = event.event_type.value.upper()
            details = ", ".join(f"{k}:{v}" for k,v in event.details.items() if v)
            
            text = f"[{dt}] {ev_type}\n{details}"
            item = QListWidgetItem(text)
            self.list_widget.addItem(item)