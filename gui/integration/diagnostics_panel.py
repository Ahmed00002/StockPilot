# gui/integration/diagnostics_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Signal
import json
from typing import Dict, Any

class DiagnosticsPanel(QWidget):
    run_diagnostics_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("System Diagnostics")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        self.btn_run = QPushButton("Run Full Diagnostics")
        self.btn_run.clicked.connect(self.run_diagnostics_requested.emit)
        layout.addWidget(self.btn_run)
        
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.text_output)

    def update_diagnostics(self, report: Dict[str, Any]):
        formatted = json.dumps(report, indent=2)
        if report.get("status") == "Healthy":
            self.text_output.setStyleSheet("font-family: monospace; font-size: 11px; color: green;")
        else:
            self.text_output.setStyleSheet("font-family: monospace; font-size: 11px; color: red;")
            
        self.text_output.setPlainText(formatted)