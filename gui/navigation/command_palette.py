# gui/navigation/command_palette.py
import logging
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from gui.widgets.icon_loader import IconLoader

logger = logging.getLogger(__name__)

class CommandPalette(QDialog):
    """A VS Code-style global command interface."""
    
    command_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
                border: 1px solid #007acc;
                border-radius: 6px;
            }
            QLineEdit {
                background-color: #3e3e42;
                border: none;
                padding: 10px;
                font-size: 16px;
                color: #ffffff;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item { padding: 10px; color: #cccccc; font-size: 14px; }
            QListWidget::item:selected { background-color: #007acc; color: #ffffff; }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command (e.g., 'Export', 'Settings')...")
        self.search_input.textChanged.connect(self._filter_commands)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.list_widget)
        
        self._populate_mock_commands()

    def _populate_mock_commands(self) -> None:
        commands = [
            ("Export: Generate Adobe CSV", "export"),
            ("View: Toggle Fullscreen", "monitor"),
            ("Metadata: Auto Generate All", "cpu"),
            ("Workspace: Open Settings", "settings"),
            ("Theme: Switch to Light Mode", "sun")
        ]
        for cmd, icon in commands:
            item = QListWidgetItem(IconLoader.get_icon(icon), cmd)
            self.list_widget.addItem(item)
            
    def _filter_commands(self, text: str) -> None:
        """Filters the command list based on input text."""
        search = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(search not in item.text().lower())

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        logger.info(f"Command Palette execution requested: {item.text()}")
        self.command_selected.emit(item.text())
        self.accept()

    def showEvent(self, event) -> None:
        self.search_input.clear()
        self.search_input.setFocus()
        super().showEvent(event)