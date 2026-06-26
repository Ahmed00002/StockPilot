# gui/image_intelligence/histogram_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRectF
import numpy as np

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 150)
        self.hist_r = None
        self.hist_g = None
        self.hist_b = None
        self.hist_luma = None

    def set_data(self, red: np.ndarray, green: np.ndarray, blue: np.ndarray, luma: np.ndarray):
        self.hist_r = red
        self.hist_g = green
        self.hist_b = blue
        self.hist_luma = luma
        self.update()

    def paintEvent(self, event):
        if self.hist_luma is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        painter.fillRect(rect, QColor(30, 30, 30))

        max_val = max(self.hist_r.max(), self.hist_g.max(), self.hist_b.max(), self.hist_luma.max())
        if max_val == 0:
            return

        width = rect.width()
        height = rect.height()

        def draw_hist(data, color):
            pen = QPen(color)
            pen.setWidthF(1.5)
            painter.setPen(pen)
            
            points = []
            for i in range(256):
                x = (i / 255.0) * width
                y = height - ((data[i] / max_val) * height)
                points.append((x, y))
                
            for i in range(255):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])

        painter.setOpacity(0.6)
        draw_hist(self.hist_r, QColor(255, 50, 50))
        draw_hist(self.hist_g, QColor(50, 255, 50))
        draw_hist(self.hist_b, QColor(50, 50, 255))
        
        painter.setOpacity(1.0)
        draw_hist(self.hist_luma, QColor(200, 200, 200))