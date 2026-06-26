# gui/integration/health_dashboard.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal
from typing import Dict, Any

class HealthDashboardWidget(QWidget):
    refresh_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel("System Health")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.btn_refresh = QPushButton("Refresh Status")
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(header_layout)
        
        self.status_container = QVBoxLayout()
        layout.addLayout(self.status_container)
        layout.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def update_health(self, statuses: Dict[str, Any]):
        self._clear_layout(self.status_container)
        
        for key, status in statuses.items():
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            
            color = "#28a745" if status.is_healthy else "#dc3545"
            bg_color = "#d4edda" if status.is_healthy else "#f8d7da"
            
            frame.setStyleSheet(f"background-color: {bg_color}; border-left: 4px solid {color}; border-radius: 3px; margin-bottom: 5px;")
            
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(10, 5, 10, 5)
            
            comp_label = QLabel(f"<b>{status.component}</b>")
            msg_label = QLabel(status.message)
            msg_label.setStyleSheet("font-size: 12px; color: #555;")
            
            f_layout.addWidget(comp_label)
            f_layout.addWidget(msg_label)
            
            self.status_container.addWidget(frame)