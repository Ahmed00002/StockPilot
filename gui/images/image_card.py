# gui/images/image_card.py
import logging
from collections import OrderedDict
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtCore import QRect, Qt, QSize, QModelIndex
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap
from image.image_model import ImageModel
from gui.images.image_status_overlay import ImageStatusOverlay
from gui.widgets.icon_loader import IconLoader

logger = logging.getLogger(__name__)

class ImageCardDelegate(QStyledItemDelegate):
    """Custom high-performance painter for Grid View thumbnails."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnail_cache: OrderedDict[str, QPixmap] = OrderedDict()
        self.max_cache_size: int = 500

    def cache_thumbnail(self, path: str, pixmap: QPixmap) -> None:
        """Safely caches a thumbnail preventing memory leaks."""
        if path in self.thumbnail_cache:
            self.thumbnail_cache.move_to_end(path)
        self.thumbnail_cache[path] = pixmap
        if len(self.thumbnail_cache) > self.max_cache_size:
            self.thumbnail_cache.popitem(last=False)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        model: ImageModel = index.data(Qt.ItemDataRole.UserRole)
        if not model:
            painter.restore()
            return
        
        # Draw Background & Selection state supporting palette theme
        is_selected = option.state & QStyle.StateFlag.State_Selected
        if is_selected:
            highlight_color = option.palette.highlight().color()
            bg_color = QColor(highlight_color.red(), highlight_color.green(), highlight_color.blue(), 60)
            painter.setBrush(bg_color)
            painter.setPen(QPen(highlight_color, 2))
        else:
            painter.setBrush(option.palette.base())
            painter.setPen(QPen(option.palette.alternateBase().color(), 1))
            
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)

        # Draw Thumbnail
        thumb_rect = QRect(rect.left() + 4, rect.top() + 4, rect.width() - 8, rect.height() - 30)
        
        # Pixmap retrieval
        if model.thumbnail_path and model.thumbnail_path in self.thumbnail_cache:
            pixmap = self.thumbnail_cache[model.thumbnail_path]
            self.thumbnail_cache.move_to_end(model.thumbnail_path)
        else:
            # Fallback icon
            pixmap = IconLoader.get_icon("image").pixmap(32, 32)
            
        if not pixmap.isNull():
            scaled_pix = pixmap.scaled(
                thumb_rect.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            # Center the image in the thumb rect
            x_offset = (thumb_rect.width() - scaled_pix.width()) // 2
            y_offset = (thumb_rect.height() - scaled_pix.height()) // 2
            painter.drawPixmap(thumb_rect.left() + x_offset, thumb_rect.top() + y_offset, scaled_pix)

        # Draw Filename text
        text_rect = QRect(rect.left() + 6, rect.bottom() - 24, rect.width() - 12, 20)
        painter.setPen(option.palette.text().color())
        fm = painter.fontMetrics()
        elided_text = fm.elidedText(model.filename or "Unknown", Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)

        # Draw Overlays (Favorites, Status)
        if getattr(model, 'is_favorite', False):
            ImageStatusOverlay.draw_badge(painter, rect, "★", "#d4af37", "top-left")
        
        status = getattr(model, 'status', "")
        if status == "Generated":
            ImageStatusOverlay.draw_badge(painter, rect, "AI", "#28a745", "top-right")
        elif status == "Error":
            ImageStatusOverlay.draw_badge(painter, rect, "!", "#f44747", "top-right")

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        return QSize(200, 200)