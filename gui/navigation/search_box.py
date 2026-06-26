# gui/navigation/search_box.py
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from gui.widgets.icon_loader import IconLoader

class SearchBox(QLineEdit):
    """Global architecture for unified search functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Search images, keywords, or commands (Ctrl+F)")
        self.setFixedWidth(300)
        self.setFixedHeight(28)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #3e3e42;
                border: 1px solid #555555;
                border-radius: 14px;
                padding-left: 30px;
                color: #ffffff;
            }
            QLineEdit:focus { border: 1px solid #007acc; }
        """)
        
        # Placeholder for search icon integration
        self.addAction(IconLoader.get_icon("search"), QLineEdit.ActionPosition.LeadingPosition)