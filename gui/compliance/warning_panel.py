# gui/compliance/warning_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class WarningPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Compliance Warnings")
        header.setStyleSheet("font-weight: bold; color: #dc3545;")
        
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.setStyleSheet("QListWidget::item { border-bottom: 1px solid #eee; padding: 5px; }")
        
        layout.addWidget(header)
        layout.addWidget(self.list_widget)

    def update_warnings(self, issues: list):
        self.list_widget.clear()
        if not issues:
            item = QListWidgetItem("No warnings. Metadata looks good.")
            item.setForeground(Qt.GlobalColor.darkGreen)
            self.list_widget.addItem(item)
            return

        for issue in issues:
            prefix = "CRITICAL: " if issue.severity.value == "Critical" else "WARNING: "
            text = f"{prefix}[{issue.category}] {issue.message}\n  → {issue.explanation}"
            item = QListWidgetItem(text)
            if issue.severity.value == "Critical":
                item.setForeground(Qt.GlobalColor.red)
            else:
                item.setForeground(Qt.GlobalColor.darkYellow)
            self.list_widget.addItem(item)