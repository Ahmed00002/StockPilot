# gui/widgets/toast_notification.py
class ToastNotification(QWidget):
    def __init__(self, message, toast_type="info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        icon = "✓" if toast_type == "success" else "⚠" if toast_type == "warning" else "ℹ"
        color = "#28a745" if toast_type == "success" else "#ffc107" if toast_type == "warning" else "#0d6efd"
        
        lbl = QLabel(f"{icon} {message}")
        lbl.setStyleSheet(f"""
            background-color: {color};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
        """)
        layout.addWidget(lbl)
        
        QTimer.singleShot(3000, self.fade_out)
    
    def fade_out(self):
        self.close()