# gui/compliance/marketplace_selector.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal

class MarketplaceSelectorWidget(QWidget):
    marketplace_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        label = QLabel("Target Marketplace:")
        label.setStyleSheet("font-weight: bold;")
        
        self.combo = QComboBox()
        self.combo.addItem("Adobe Stock", "adobe_stock")
        self.combo.currentIndexChanged.connect(self._on_change)
        
        layout.addWidget(label)
        layout.addWidget(self.combo)
        layout.addStretch()

    def _on_change(self):
        data = self.combo.currentData()
        self.marketplace_changed.emit(data)