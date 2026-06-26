# gui/description/description_score_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class DescriptionScoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        self.score_label = QLabel("Description Quality: 0")
        self.score_label.setStyleSheet("font-weight: bold;")
        
        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(0)
        self.score_bar.setTextVisible(False)
        self.score_bar.setFixedHeight(8)
        
        details_layout = QHBoxLayout()
        self.seo_label = QLabel("SEO: 0")
        self.comm_label = QLabel("Commercial: 0")
        self.read_label = QLabel("Readability: 0")
        
        details_layout.addWidget(self.seo_label)
        details_layout.addWidget(self.comm_label)
        details_layout.addWidget(self.read_label)
        
        layout.addWidget(self.score_label)
        layout.addWidget(self.score_bar)
        layout.addLayout(details_layout)

    def update_scores(self, overall: float, seo: float, comm: float, readability: float):
        self.score_label.setText(f"Description Quality: {int(overall)}")
        self.score_bar.setValue(int(overall))
        
        if overall >= 80:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: #28a745; }")
        elif overall >= 50:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffc107; }")
        else:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: #dc3545; }")

        self.seo_label.setText(f"SEO: {int(seo)}")
        self.comm_label.setText(f"Commercial: {int(comm)}")
        self.read_label.setText(f"Readability: {int(readability)}")