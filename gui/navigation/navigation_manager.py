# gui/navigation/navigation_manager.py
import logging
from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import QObject, Signal
from gui.navigation.page_router import PageRouter
from gui.navigation.sidebar import Sidebar
from gui.navigation.breadcrumb import BreadcrumbWidget

logger = logging.getLogger(__name__)

class NavigationManager(QObject):
    """Central orchestrator tying the Sidebar, Router, and Breadcrumbs together."""
    
    page_changed = Signal(str)

    def __init__(self, stack_widget: QStackedWidget, sidebar: Sidebar, breadcrumb: BreadcrumbWidget) -> None:
        super().__init__()
        self.router = PageRouter(stack_widget)
        self.sidebar = sidebar
        self.breadcrumb = breadcrumb
        
        self.sidebar.navigation_requested.connect(self.navigate)

    def register_page(self, page_id: str, widget: QWidget, title: str) -> None:
        """Registers a page and stores its UI title mapping."""
        self.router.register_page(page_id, widget)
        # In a full implementation, the title would be stored in a registry 
        # to update the breadcrumb properly.

    def navigate(self, page_id: str) -> None:
        """Coordinates the UI transition across all navigation components."""
        if self.router.navigate_to(page_id):
            self.sidebar.set_active_page(page_id)
            self._update_breadcrumb(page_id)
            self.page_changed.emit(page_id)

    def _update_breadcrumb(self, page_id: str) -> None:
        """Translates the internal page_id to a displayable breadcrumb path."""
        # Mock logic. Normally driven by a hierarchy map.
        title = page_id.replace("_", " ").title()
        self.breadcrumb.set_path(["Workspace", title])