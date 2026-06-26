# gui/image_intelligence/technical_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PySide6.QtCore import Qt

class TechnicalPanel(QWidget):
    """Displays technical image metadata from TechnicalAnalyzer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._clear_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Technical Information")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(title)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 4px;")
        grid = QGridLayout(info_frame)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(8)
        
        self.labels = {}
        rows = [
            ("Dimensions", "dimensions"),
            ("Aspect Ratio", "aspect_ratio"),
            ("Megapixels", "megapixels"),
            ("Color Space", "color_space"),
            ("Bit Depth", "bit_depth"),
            ("DPI", "dpi"),
            ("File Type", "file_type"),
            ("File Size", "file_size")
        ]
        
        for i, (label_text, key) in enumerate(rows):
            lbl_name = QLabel(label_text + ":")
            lbl_name.setStyleSheet("color: #858585; font-size: 12px;")
            lbl_value = QLabel("--")
            lbl_value.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold;")
            lbl_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            grid.addWidget(lbl_name, i, 0)
            grid.addWidget(lbl_value, i, 1)
            self.labels[key] = lbl_value
        
        layout.addWidget(info_frame)
        
        self.status_label = QLabel("No image loaded")
        self.status_label.setStyleSheet("color: #858585; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

    def set_technical_data(self, tech_data):
        """Set technical data from TechnicalData."""
        if not tech_data:
            self._clear_data()
            return
        
        self.labels["dimensions"].setText(f"{tech_data.width} × {tech_data.height}")
        self.labels["aspect_ratio"].setText(f"{tech_data.aspect_ratio:.2f}")
        self.labels["megapixels"].setText(f"{tech_data.megapixels:.2f} MP")
        self.labels["color_space"].setText(tech_data.color_space)
        self.labels["bit_depth"].setText(f"{tech_data.bit_depth}-bit")
        self.labels["dpi"].setText(f"{tech_data.dpi[0]} × {tech_data.dpi[1]}")
        self.labels["file_type"].setText(tech_data.file_signature)
        
        size_kb = tech_data.file_size_bytes / 1024
        size_mb = size_kb / 1024
        if size_mb >= 1:
            self.labels["file_size"].setText(f"{size_mb:.2f} MB")
        else:
            self.labels["file_size"].setText(f"{size_kb:.1f} KB")
        
        self.status_label.setText("Technical analysis complete")

    def _clear_data(self):
        for lbl in self.labels.values():
            lbl.setText("--")
        self.status_label.setText("No image loaded")

    def clear(self):
        """Clear all technical data."""
        self._clear_data()