# gui/title/title_score_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class TitleScoreWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.score_label = QLabel("Overall Quality: 0")
        self.score_label.setStyleSheet("font-weight: bold;")
        
        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(0)
        self.score_bar.setTextVisible(False)
        self.score_bar.setFixedHeight(10)
        
        self.seo_label = QLabel("SEO Score: 0")
        self.comm_label = QLabel("Commercial Value: 0")
        
        layout.addWidget(self.score_label)
        layout.addWidget(self.score_bar)
        layout.addWidget(self.seo_label)
        layout.addWidget(self.comm_label)

    def update_scores(self, overall: float, seo: float, comm: float):
        self.score_label.setText(f"Overall Quality: {int(overall)}")
        self.score_bar.setValue(int(overall))
        
        if overall >= 80:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif overall >= 50:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.score_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")

        self.seo_label.setText(f"SEO Score: {int(seo)}")
        self.comm_label.setText(f"Commercial Value: {int(comm)}")