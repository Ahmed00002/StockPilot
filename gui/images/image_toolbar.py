# gui/images/image_toolbar.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QComboBox
from PySide6.QtCore import Qt
from gui.widgets.icon_loader import IconLoader

class ImageToolbar(QWidget):
    """Controls for sorting, filtering, and zoom scale mapping to the Grid."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #252526; border-bottom: 1px solid #3f3f46;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        self.btn_import = QPushButton(IconLoader.get_icon("import"), "Import")
        self.btn_import.setStyleSheet("background-color: #007acc; color: white; border: none; padding: 4px 12px; border-radius: 4px;")
        layout.addWidget(self.btn_import)
        
        layout.addWidget(QLabel("Sort by:"))
        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems(["Filename", "Date Added", "Resolution", "Rating"])
        self.cmb_sort.setStyleSheet("background-color: #3e3e42; color: white; border: none; padding: 2px;")
        layout.addWidget(self.cmb_sort)
        
        layout.addStretch()
        
        layout.addWidget(QLabel("Zoom:"))
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(100, 400)
        self.slider_zoom.setValue(200)
        self.slider_zoom.setFixedWidth(150)
        layout.addWidget(self.slider_zoom)