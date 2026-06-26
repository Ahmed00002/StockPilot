# gui/navigation/page_router.py
import logging
from typing import Dict, List, Optional
from PySide6.QtWidgets import QStackedWidget, QWidget

logger = logging.getLogger(__name__)

class PageRouter:
    """Manages the creation, caching, and switching of central workspace views."""
    
    def __init__(self, stack_widget: QStackedWidget) -> None:
        self.stack = stack_widget
        self.pages: Dict[str, QWidget] = {}
        self.history: List[str] = []
        self._current_page_id: Optional[str] = None

    def register_page(self, page_id: str, page_widget: QWidget) -> None:
        """Adds a page instance to the router stack."""
        if page_id in self.pages:
            logger.warning(f"Page '{page_id}' is already registered. Overwriting.")
            self.stack.removeWidget(self.pages[page_id])
            
        self.pages[page_id] = page_widget
        self.stack.addWidget(page_widget)
        logger.debug(f"Registered page: {page_id}")

    def navigate_to(self, page_id: str) -> bool:
        """Switches the view to the requested page."""
        if page_id not in self.pages:
            logger.error(f"Attempted to navigate to unknown page: {page_id}")
            return False

        if self._current_page_id == page_id:
            return True

        if self._current_page_id:
            self.history.append(self._current_page_id)
            
        self._current_page_id = page_id
        self.stack.setCurrentWidget(self.pages[page_id])
        logger.info(f"Navigated to: {page_id}")
        return True

    def navigate_back(self) -> bool:
        """Restores the previous page in the history stack."""
        if not self.history:
            return False
            
        previous_page = self.history.pop()
        self._current_page_id = previous_page
        self.stack.setCurrentWidget(self.pages[previous_page])
        logger.info(f"Navigated back to: {previous_page}")
        return True

    def get_current_page_id(self) -> Optional[str]:
        return self._current_page_id