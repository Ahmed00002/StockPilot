# gui/images/image_properties_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QFrame
from PySide6.QtCore import Qt
from image.image_model import ImageModel

class ImagePropertiesPanel(QFrame):
    """Right-side inspector displaying metadata values for the active selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QFrame { background-color: #252526; border-left: 1px solid #3f3f46; color: #cccccc; }
            QLabel { font-size: 12px; }
            QLabel#Title { font-weight: bold; color: #ffffff; font-size: 14px; margin-top: 10px; }
        """)
        
        layout = QVBoxLayout(self)
        
        lbl_header = QLabel("Properties")
        lbl_header.setObjectName("Title")
        layout.addWidget(lbl_header)
        
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.lbl_name = QLabel("--")
        self.lbl_res = QLabel("--")
        self.lbl_size = QLabel("--")
        self.lbl_format = QLabel("--")
        self.lbl_date = QLabel("--")
        
        self.form.addRow("Name:", self.lbl_name)
        self.form.addRow("Resolution:", self.lbl_res)
        self.form.addRow("Size:", self.lbl_size)
        self.form.addRow("Format:", self.lbl_format)
        self.form.addRow("Imported:", self.lbl_date)
        
        layout.addLayout(self.form)
        layout.addStretch()

    def set_model(self, model: ImageModel) -> None:
        """Alias to synchronize with ImagesPage selection API."""
        self.update_properties(model)

    def update_properties(self, model: ImageModel) -> None:
        if not model:
            self.lbl_name.setText("--")
            self.lbl_res.setText("--")
            self.lbl_size.setText("--")
            self.lbl_format.setText("--")
            self.lbl_date.setText("--")
            return
            
        self.lbl_name.setText(model.filename)
        self.lbl_res.setText(f"{model.width} x {model.height}")
        self.lbl_size.setText(f"{round(model.file_size_bytes / 1024 / 1024, 2)} MB")
        self.lbl_format.setText(model.format)
        self.lbl_date.setText(model.imported_date[:10] if hasattr(model, 'imported_date') else "Unknown")