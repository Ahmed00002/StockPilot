# gui/ai/routing_rules_widget.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QListWidget
from PySide6.QtCore import Qt

from ai.orchestration.routing_engine import RoutingStrategy
from ai.orchestration.provider_priority import ProviderPriority

class RoutingRulesWidget(QWidget):
    """Configuration panel to manage global routing behaviors and prioritization."""

    def __init__(self, priority_manager: ProviderPriority, parent=None):
        super().__init__(parent)
        self.priority_manager = priority_manager
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Strategy Selector
        strat_layout = QHBoxLayout()
        strat_layout.addWidget(QLabel("Global Routing Strategy:"))
        self.cb_strategy = QComboBox()
        self.cb_strategy.addItems([s.value for s in RoutingStrategy])
        self.cb_strategy.setCurrentText("balanced")
        strat_layout.addWidget(self.cb_strategy)
        layout.addLayout(strat_layout)
        
        # Priority List
        layout.addWidget(QLabel("Provider Priority Order (Top-Down):"))
        self.list_priority = QListWidget()
        self.list_priority.setDragDropMode(QListWidget.InternalMove)
        
        for p in self.priority_manager.get_priority_list():
            self.list_priority.addItem(p)
            
        layout.addWidget(self.list_priority)
        
        # Save Button
        self.btn_save = QPushButton("Apply Routing Rules")
        self.btn_save.clicked.connect(self._save_rules)
        layout.addWidget(self.btn_save)

    def _save_rules(self):
        new_order = [self.list_priority.item(i).text() for i in range(self.list_priority.count())]
        self.priority_manager.set_priority_list(new_order)
        # Note: Strategy saving logic would map to global application settings.