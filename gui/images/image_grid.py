# gui/images/image_grid.py
import logging
from typing import List
from PySide6.QtWidgets import QListView, QAbstractItemView
from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QSize
from image.image_model import ImageModel
from gui.images.image_card import ImageCardDelegate

logger = logging.getLogger(__name__)

class ImageListModel(QAbstractListModel):
    """Virtual model feeding data to the List View without holding images in RAM."""
    def __init__(self, images: List[ImageModel] = None, parent=None):
        super().__init__(parent)
        self.images = images or []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.images)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.images)):
            return None
            
        model = self.images[index.row()]
        
        if role == Qt.ItemDataRole.UserRole:
            return model
        return None

    def update_data(self, new_images: List[ImageModel]) -> None:
        self.beginResetModel()
        self.images = new_images
        self.endResetModel()


class ImageGrid(QListView):
    """Infinite-scroll capable virtual grid view."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ImageGrid")
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setSpacing(10)
        
        self.setStyleSheet("""
            QListView {
                background-color: #1e1e1e;
                border: none;
                outline: none;
            }
        """)
        
        self.delegate = ImageCardDelegate(self)
        self.setItemDelegate(self.delegate)
        self.setGridSize(QSize(200, 200)) # Default

    def set_zoom_level(self, size: int) -> None:
        """Dynamically adjusts cell size constraints from the UI slider."""
        self.setGridSize(QSize(size, size))
        self.update()