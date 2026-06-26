# gui/compliance/upload_readiness_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from metadata.compliance.compliance_models import ComplianceStatus

class UploadReadinessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("border-radius: 5px; padding: 10px;")
        sf_layout = QVBoxLayout(self.status_frame)
        sf_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Readiness: UNKNOWN")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.score_label = QLabel("Score: 0")
        self.score_label.setStyleSheet("font-size: 14px; color: white;")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sf_layout.addWidget(self.status_label)
        sf_layout.addWidget(self.score_label)
        
        layout.addWidget(self.status_frame)

    def update_status(self, status: ComplianceStatus, score: float):
        self.score_label.setText(f"Overall Score: {int(score)}")
        self.status_label.setText(f"Status: {status.value.upper()}")
        
        if status == ComplianceStatus.READY:
            self.status_frame.setStyleSheet("background-color: #28a745; border-radius: 5px; padding: 10px;")
        elif status == ComplianceStatus.NEEDS_REVIEW:
            self.status_frame.setStyleSheet("background-color: #17a2b8; border-radius: 5px; padding: 10px;")
        elif status == ComplianceStatus.MAJOR_ISSUES:
            self.status_frame.setStyleSheet("background-color: #ffc107; border-radius: 5px; padding: 10px;")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
            self.score_label.setStyleSheet("font-size: 14px; color: #333;")
        else:
            self.status_frame.setStyleSheet("background-color: #dc3545; border-radius: 5px; padding: 10px;")