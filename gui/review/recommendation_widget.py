# gui/review/recommendation_widget.py
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt

class RecommendationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Review Feedback")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def update_recommendations(self, report: Any):
        self._clear_layout(self.content_layout)
        
        all_items = report.critical_errors + report.warnings + report.recommendations
        
        if not all_items:
            lbl = QLabel("No issues found. Metadata is optimized!")
            lbl.setStyleSheet("color: green; font-style: italic;")
            self.content_layout.addWidget(lbl)
            return

        for item in all_items:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            
            color = "#dc3545" if item.severity.value == "critical" else "#ffc107" if item.severity.value == "warning" else "#17a2b8"
            bg_color = "#f8d7da" if item.severity.value == "critical" else "#fff3cd" if item.severity.value == "warning" else "#d1ecf1"
            
            frame.setStyleSheet(f"background-color: {bg_color}; border-left: 4px solid {color}; border-radius: 3px;")
            
            f_layout = QVBoxLayout(frame)
            f_layout.setContentsMargins(5, 5, 5, 5)
            
            title = QLabel(f"<b>[{item.category}]</b> {item.message}")
            title.setWordWrap(True)
            f_layout.addWidget(title)
            
            desc = QLabel(item.explanation)
            desc.setStyleSheet("font-size: 11px; color: #555;")
            desc.setWordWrap(True)
            f_layout.addWidget(desc)
            
            self.content_layout.addWidget(frame)
