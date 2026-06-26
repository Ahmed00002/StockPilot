# gui/workspace/revision_statistics_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout
from PySide6.QtCore import Qt

class RevisionStatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Workspace Statistics")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        self.form_layout = QFormLayout()
        
        self.lbl_total = QLabel("0")
        self.lbl_merges = QLabel("0")
        self.lbl_manual = QLabel("0")
        self.lbl_avg_score = QLabel("0.0")
        self.lbl_best_score = QLabel("0.0")
        
        self.form_layout.addRow("Total Versions:", self.lbl_total)
        self.form_layout.addRow("Merges:", self.lbl_merges)
        self.form_layout.addRow("Manual Edits:", self.lbl_manual)
        self.form_layout.addRow("Average Score:", self.lbl_avg_score)
        self.form_layout.addRow("Best Score:", self.lbl_best_score)
        
        layout.addLayout(self.form_layout)
        layout.addStretch()

    def update_stats(self, stats: any):
        self.lbl_total.setText(str(stats.total_versions))
        self.lbl_merges.setText(str(stats.merge_count))
        self.lbl_manual.setText(str(stats.manual_edits))
        self.lbl_avg_score.setText(f"{stats.average_score:.1f}")
        self.lbl_best_score.setText(f"{stats.best_score:.1f}")