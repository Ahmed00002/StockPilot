# gui/review/quality_widget.py
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class QualityScoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.overall_label = QLabel("Overall Quality: 0")
        self.overall_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.overall_bar = QProgressBar()
        self.overall_bar.setRange(0, 100)
        self.overall_bar.setValue(0)
        self.overall_bar.setFixedHeight(15)
        self.overall_bar.setTextVisible(False)
        
        layout.addWidget(self.overall_label)
        layout.addWidget(self.overall_bar)
        
        self.details_layout = QVBoxLayout()
        layout.addLayout(self.details_layout)

        self.component_labels = {}
        components = ["SEO", "Commercial", "Grammar", "Readability", "Marketplace", "Confidence"]
        
        for comp in components:
            row = QHBoxLayout()
            lbl = QLabel(f"{comp}:")
            lbl.setFixedWidth(100)
            val = QLabel("0")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            self.component_labels[comp.lower()] = val
            self.details_layout.addLayout(row)

    def _get_color_style(self, score: float) -> str:
        if score >= 85: return "color: green; font-weight: bold;"
        if score >= 60: return "color: orange; font-weight: bold;"
        return "color: red; font-weight: bold;"

    def update_scores(self, report: Any):
        overall = int(report.overall_score)
        self.overall_label.setText(f"Overall Quality: {overall}")
        self.overall_bar.setValue(overall)
        
        if overall >= 85:
            self.overall_bar.setStyleSheet("QProgressBar::chunk { background-color: #28a745; }")
        elif overall >= 60:
            self.overall_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffc107; }")
        else:
            self.overall_bar.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")

        comps = report.component_scores
        data = {
            "seo": comps.seo,
            "commercial": comps.commercial,
            "grammar": comps.grammar,
            "readability": comps.readability,
            "marketplace": comps.marketplace,
            "confidence": comps.confidence
        }
        
        for key, val_label in self.component_labels.items():
            score = int(data.get(key, 0))
            val_label.setText(str(score))
            val_label.setStyleSheet(self._get_color_style(score))
