# image/selection_manager.py
from typing import Set, List
from PySide6.QtCore import QObject, Signal

class SelectionManager(QObject):
    """Manages the state of currently selected items in the UI."""
    
    selection_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self._selected_ids: Set[str] = set()

    def set_selection(self, image_ids: List[str]) -> None:
        self._selected_ids = set(image_ids)
        self.selection_changed.emit(list(self._selected_ids))

    def add_to_selection(self, image_id: str) -> None:
        if image_id not in self._selected_ids:
            self._selected_ids.add(image_id)
            self.selection_changed.emit(list(self._selected_ids))

    def remove_from_selection(self, image_id: str) -> None:
        if image_id in self._selected_ids:
            self._selected_ids.remove(image_id)
            self.selection_changed.emit(list(self._selected_ids))

    def clear(self) -> None:
        if self._selected_ids:
            self._selected_ids.clear()
            self.selection_changed.emit([])

    def get_selected(self) -> List[str]:
        return list(self._selected_ids)