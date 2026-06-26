# gui/images/image_status_overlay.py
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import QRect, Qt

class ImageStatusOverlay:
    """Helper class to draw badge indicators on thumbnails safely inside delegates."""

    @staticmethod
    def draw_badge(painter: QPainter, rect: QRect, text: str, color_hex: str, position: str = "top-right") -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg_color = QColor(color_hex)
        bg_color.setAlpha(200)
        
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()
        
        pad = 4
        badge_w = text_width + (pad * 2)
        badge_h = text_height + (pad * 2)
        
        x, y = 0, 0
        if position == "top-right":
            x = rect.right() - badge_w - 4
            y = rect.top() + 4
        elif position == "top-left":
            x = rect.left() + 4
            y = rect.top() + 4
        elif position == "bottom-right":
            x = rect.right() - badge_w - 4
            y = rect.bottom() - badge_h - 4
            
        bg_rect = QRect(x, y, badge_w, badge_h)
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()