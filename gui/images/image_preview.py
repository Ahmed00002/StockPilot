# gui/images/image_preview.py
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtCore import Qt

class ImagePreviewWidget(QWidget):
    """High-performance QGraphicsView designed for zooming and panning high-res images."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setStyleSheet("border: none;")
        
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        layout.addWidget(self.view)
        
        self.lbl_info = QLabel("No Image Selected")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet("color: #858585; padding: 10px;")
        layout.addWidget(self.lbl_info)

    def load_image(self, qimage: QImage, filename: str) -> None:
        pixmap = QPixmap.fromImage(qimage)
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.lbl_info.setText(filename)

    def set_image(self, model) -> None:
        """Convenience method to load from an ImageModel or clear the view."""
        if not model.absolute_path or not Path(model.absolute_path).exists():
            self.lbl_info.setText(f"Image file not found: {model.filename}")
            self.pixmap_item.setPixmap(QPixmap())
            return
            
        img = QImage(str(model.absolute_path))
        if img.isNull():
            self.lbl_info.setText(f"Failed to load: {model.filename}")
            return