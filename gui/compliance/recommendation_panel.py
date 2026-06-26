# gui/compliance/recommendation_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class RecommendationPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Actionable Recommendations")
        header.setStyleSheet("font-weight: bold; color: #17a2b8;")
        
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)
        self.list_widget.setStyleSheet("QListWidget::item { border-bottom: 1px solid #eee; padding: 5px; }")
        
        layout.addWidget(header)
        layout.addWidget(self.list_widget)

    def update_recommendations(self, issues: list):
        self.list_widget.clear()
        if not issues:
            item = QListWidgetItem("No recommendations required.")
            item.setForeground(Qt.GlobalColor.gray)
            self.list_widget.addItem(item)
            return

        for issue in issues:
            text = f"💡 [{issue.category}] {issue.message}"
            item = QListWidgetItem(text)
            item.setForeground(Qt.GlobalColor.black)
            self.list_widget.addItem(item)