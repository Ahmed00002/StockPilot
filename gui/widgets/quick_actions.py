# gui/widgets/quick_actions.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout
from PySide6.QtCore import Qt, Signal
from gui.widgets.icon_loader import IconLoader

class QuickActionsWidget(QWidget):
    """Provides fast access to primary application workflows."""

    action_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_title = QLabel("Quick Actions")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        actions = [
            ("Import Images", "import", "images"),
            ("Generate Metadata", "cpu", "metadata"),
            ("Compare AI", "columns", "ai_studio"),
            ("Export CSV", "export", "export")
        ]
        
        for i, (text, icon, page_id) in enumerate(actions):
            btn = QPushButton(IconLoader.get_icon(icon), text)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, target=page_id: self.action_requested.emit(target))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d30;
                    border: 1px solid #3f3f46;
                    border-radius: 4px;
                    text-align: left;
                    padding-left: 10px;
                }
                QPushButton:hover { background-color: #3e3e42; border: 1px solid #007acc; }
            """)
            grid.addWidget(btn, i // 2, i % 2)
            
        layout.addLayout(grid)
