# gui/image_intelligence/metadata_viewer.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, 
                              QTreeWidgetItem, QHeaderView)
from image.intelligence.metadata_reader import ImageMetadata

class MetadataViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.layout.addWidget(self.tree)

    def populate(self, metadata: ImageMetadata):
        self.tree.clear()
        
        # EXIF Node
        exif_item = QTreeWidgetItem(self.tree, ["EXIF"])
        for field in metadata.exif.__dataclass_fields__:
            val = getattr(metadata.exif, field)
            if val:
                QTreeWidgetItem(exif_item, [field.replace("_", " ").title(), str(val)])
                
        # IPTC Node
        iptc_item = QTreeWidgetItem(self.tree, ["IPTC"])
        for field in metadata.iptc.__dataclass_fields__:
            val = getattr(metadata.iptc, field)
            if val:
                QTreeWidgetItem(iptc_item, [field.replace("_", " ").title(), str(val)])

        # XMP Node
        xmp_item = QTreeWidgetItem(self.tree, ["XMP"])
        for key, val in metadata.xmp.raw_namespaces.items():
            if val:
                QTreeWidgetItem(xmp_item, [key.replace("XMP:", ""), str(val)])
                
        self.tree.expandAll()