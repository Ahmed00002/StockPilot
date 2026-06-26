# gui/image_intelligence/color_palette_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

class ColorPaletteWidget(QWidget):
    """Visual color palette analyzer displaying dominant image colors."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.colors = []

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Dominant Color Palette")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(title)
        
        self.color_frame = QFrame()
        self.color_frame.setMinimumHeight(120)
        self.color_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
        color_layout = QVBoxLayout(self.color_frame)
        color_layout.setContentsMargins(8, 8, 8, 8)
        
        self.color_display = QLabel()
        self.color_display.setAlignment(Qt.AlignCenter)
        self.color_display.setMinimumHeight(80)
        self.color_display.setStyleSheet("background-color: transparent;")
        color_layout.addWidget(self.color_display)
        
        layout.addWidget(self.color_frame)
        
        self.info_label = QLabel("No image loaded")
        self.info_label.setStyleSheet("color: #858585; font-style: italic;")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

    def set_colors(self, colors: list):
        """Set dominant colors from image analysis. Colors should be RGB tuples."""
        self.colors = colors
        if not colors:
            self.info_label.setText("No colors detected")
            self.color_display.clear()
            return
        
        self.info_label.setText(f"{len(colors)} dominant colors detected")
        
        # Create a visual representation of colors
        width = 300
        height = 80
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        block_width = width // len(colors)
        for i, color in enumerate(colors):
            if isinstance(color, tuple) and len(color) >= 3:
                qcolor = QColor(color[0], color[1], color[2])
            else:
                qcolor = QColor(color)
            painter.fillRect(i * block_width, 0, block_width, height, qcolor)
        
        painter.end()
        self.color_display.setPixmap(pixmap)

    def clear(self):
        """Clear the color display."""
        self.colors = []
        self.info_label.setText("No image loaded")
        self.color_display.clear()
