# gui/images/image_context_menu.py
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from gui.widgets.icon_loader import IconLoader

class ImageContextMenu(QMenu):
    """Popup context menu available via right-click on Image Grid items."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu { background-color: #2d2d30; color: #cccccc; border: 1px solid #3f3f46; }
            QMenu::item:selected { background-color: #007acc; color: white; }
        """)
        
        self.act_open = QAction("Open in Preview", self)
        self.act_reveal = QAction("Reveal in Explorer", self)
        self.act_fav = QAction(IconLoader.get_icon("star"), "Toggle Favorite", self)
        self.act_delete = QAction(IconLoader.get_icon("trash"), "Remove from Workspace", self)
        
        self.addAction(self.act_open)
        self.addAction(self.act_reveal)
        self.addSeparator()
        self.addAction(self.act_fav)
        self.addSeparator()
        self.addAction(self.act_delete)