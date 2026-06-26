# gui/integration/performance_monitor.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QFormLayout
from PySide6.QtCore import Qt
from typing import Dict

class PerformanceMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Pipeline Performance")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        layout.addStretch()
        
        self.bars = {}

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.bars.clear()

    def update_performance(self, averages: Dict[str, float]):
        self._clear_layout(self.form_layout)
        
        if not averages:
            lbl = QLabel("No performance data available.")
            lbl.setStyleSheet("color: gray; font-style: italic;")
            self.form_layout.addRow(lbl)
            return

        max_duration = max(averages.values()) if averages.values() else 1.0
        
        for stage, duration in averages.items():
            bar = QProgressBar()
            bar.setRange(0, 100)
            pct = int((duration / max_duration) * 100) if max_duration > 0 else 0
            bar.setValue(pct)
            bar.setFormat(f"{duration:.2f}s")
            bar.setFixedHeight(15)
            
            if pct > 80:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")
            elif pct > 50:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #ffc107; }")
            else:
                bar.setStyleSheet("QProgressBar::chunk { background-color: #28a745; }")
                
            self.bars[stage] = bar
            self.form_layout.addRow(f"{stage.capitalize()}:", bar)