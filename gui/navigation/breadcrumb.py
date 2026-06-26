# gui/navigation/breadcrumb.py
from typing import List
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class BreadcrumbWidget(QWidget):
    """Displays the hierarchical path of the current navigation context."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        self.path_labels: List[QLabel] = []
        self.set_path(["Dashboard"])

    def set_path(self, path_nodes: List[str]) -> None:
        """Updates the breadcrumb trail."""
        for i in reversed(range(self.layout.count())): 
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        self.path_labels.clear()
        
        for index, node in enumerate(path_nodes):
            lbl = QLabel(node)
            if index == len(path_nodes) - 1:
                lbl.setStyleSheet("color: #ffffff; font-weight: bold;")
            else:
                lbl.setStyleSheet("color: #cccccc;")
            self.layout.addWidget(lbl)
            self.path_labels.append(lbl)
            
            if index < len(path_nodes) - 1:
                sep = QLabel(">")
                sep.setStyleSheet("color: #555555;")
                self.layout.addWidget(sep)