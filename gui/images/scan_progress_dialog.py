# gui/images/scan_progress_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import Qt

class ScanProgressDialog(QDialog):
    """Modal dialog displaying asynchronous indexing feedback."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing Images")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setStyleSheet("QDialog { background-color: #252526; color: white; }")
        
        layout = QVBoxLayout(self)
        
        self.lbl_status = QLabel("Scanning files...")
        layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #3e3e42; color: white;")
        layout.addWidget(self.btn_cancel, alignment=Qt.AlignmentFlag.AlignRight)

    def update_progress(self, current: int, total: int, message: str) -> None:
        self.lbl_status.setText(message)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)