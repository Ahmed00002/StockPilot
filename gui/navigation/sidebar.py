# gui/navigation/sidebar.py
import logging
from typing import Dict
from PySide6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Property, QPropertyAnimation, QEasingCurve
from gui.navigation.sidebar_item import SidebarItem

logger = logging.getLogger(__name__)

class Sidebar(QFrame):
    """The master navigation panel rendering the primary application sections."""
    
    navigation_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LeftSidebar")
        self._is_collapsed = False
        self._current_width = 240
        self.items: Dict[str, SidebarItem] = {}
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(4)
        
        self._build_items()
        self.setFixedWidth(self._current_width)
        
        self.anim_width = QPropertyAnimation(self, b"current_width")
        self.anim_width.setDuration(200)
        self.anim_width.setEasingCurve(QEasingCurve.Type.InOutCubic)

    @Property(int)
    def current_width(self) -> int:
        return self._current_width

    @current_width.setter
    def current_width(self, width: int) -> None:
        self._current_width = width
        self.setFixedWidth(width)

    def _build_items(self) -> None:
        nav_structure = [
            ("dashboard", "Dashboard", "dashboard"),
            ("workspaces", "Workspaces", "folder"),
            ("images", "Images", "image"),
            ("metadata", "Metadata Studio", "edit"),
            ("ai_studio", "AI Studio", "cpu"),
            ("seo", "SEO Engine", "bar-chart"),
            ("export", "Export Center", "export"),
            ("history", "History", "history"),
            ("analytics", "Analytics", "activity"),
            ("spacer", "", ""),
            ("settings", "Settings", "settings"),
            ("plugins", "Plugins", "box"),
            ("logs", "Logs", "align-left"),
            ("help", "Help", "help-circle")
        ]

        for page_id, label, icon in nav_structure:
            if page_id == "spacer":
                spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
                self.layout.addItem(spacer)
            else:
                item = SidebarItem(page_id, label, icon)
                item.clicked.connect(self._on_item_clicked)
                self.layout.addWidget(item)
                self.items[page_id] = item

    def _on_item_clicked(self, page_id: str) -> None:
        self.set_active_page(page_id)
        self.navigation_requested.emit(page_id)

    def set_active_page(self, page_id: str) -> None:
        """Visually marks the correct sidebar item as active."""
        for pid, item in self.items.items():
            item.set_selected(pid == page_id)
            
    def toggle_collapse(self) -> None:
        """Animates the sidebar between expanded and collapsed states."""
        self._is_collapsed = not self._is_collapsed
        
        for item in self.items.values():
            item.set_collapsed(self._is_collapsed)
            
        target_width = 60 if self._is_collapsed else 240
        
        self.anim_width.setStartValue(self.width())
        self.anim_width.setEndValue(target_width)
        self.anim_width.start()
        
        logger.debug(f"Sidebar collapsed state toggled to: {self._is_collapsed}")