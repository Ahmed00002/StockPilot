# gui/images/image_card.py
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PySide6.QtCore import QRect, Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap
from image.image_model import ImageModel
from gui.images.image_status_overlay import ImageStatusOverlay
from gui.widgets.icon_loader import IconLoader

class ImageCardDelegate(QStyledItemDelegate):
    """Custom high-performance painter for Grid View thumbnails."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumbnail_cache = {} # memory mapped Pixmaps

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = option.rect
        model: ImageModel = index.data(Qt.ItemDataRole.UserRole)
        
        # Draw Background & Selection state
        is_selected = option.state & QStyle.StateFlag.State_Selected
        if is_selected:
            painter.setBrush(QColor(0, 122, 204, 100))
            painter.setPen(QPen(QColor(0, 122, 204), 2))
        else:
            painter.setBrush(QColor(37, 37, 38))
            painter.setPen(QPen(QColor(63, 63, 70), 1))
            
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)

        # Draw Thumbnail
        thumb_rect = QRect(rect.left() + 4, rect.top() + 4, rect.width() - 8, rect.height() - 30)
        
        # Pixmap retrieval (mock logic expects valid paths, handles empty gracefully)
        if model.thumbnail_path and model.thumbnail_path in self.thumbnail_cache:
            pixmap = self.thumbnail_cache[model.thumbnail_path]
        else:
            # Fallback icon
            pixmap = IconLoader.get_icon("image").pixmap(32, 32)
            
        scaled_pix = pixmap.scaled(thumb_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Center the image in the thumb rect
        x_offset = (thumb_rect.width() - scaled_pix.width()) // 2
        y_offset = (thumb_rect.height() - scaled_pix.height()) // 2
        painter.drawPixmap(thumb_rect.left() + x_offset, thumb_rect.top() + y_offset, scaled_pix)

        # Draw Filename text
        text_rect = QRect(rect.left() + 6, rect.bottom() - 24, rect.width() - 12, 20)
        painter.setPen(QColor(204, 204, 204))
        fm = painter.fontMetrics()
        elided_text = fm.elidedText(model.filename, Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)

        # Draw Overlays (Favorites, Status)
        if model.is_favorite:
            ImageStatusOverlay.draw_badge(painter, rect, "★", "#d4af37", "top-left")
        
        if model.status == "Generated":
            ImageStatusOverlay.draw_badge(painter, rect, "AI", "#28a745", "top-right")

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        # Driven by external slider, default return
        return QSize(200, 200)