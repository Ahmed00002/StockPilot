# gui/ai/usage_dashboard.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt, QObject, Signal, Slot

class UsageSignals(QObject):
    usage_updated = Signal()

class UsageDashboard(QWidget):
    """Provides high-level insights into token consumption and financial costs."""

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        # INTEGRATION FIX: Standardized DI container approach
        self.container = container
        self.signals = UsageSignals()
        self._setup_ui()
        self._connect_events()
        
        # Initial display setup
        self._update_display()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Global Usage Analytics")
        form = QFormLayout()
        
        self.lbl_reqs = QLabel("0")
        self.lbl_success = QLabel("0.0%")
        self.lbl_tokens = QLabel("0")
        self.lbl_cost = QLabel("$0.00")
        
        form.addRow("Total Requests:", self.lbl_reqs)
        form.addRow("Success Rate:", self.lbl_success)
        form.addRow("Tokens Processed:", self.lbl_tokens)
        form.addRow("Estimated Cost:", self.lbl_cost)
        
        group.setLayout(form)
        layout.addWidget(group)
        layout.addStretch()

    def _connect_events(self):
        self.signals.usage_updated.connect(self._update_display)
        
        if not self.container: return
        events = self.container.get_service("orchestration_events")
        if events:
            # INTEGRATION FIX: Replaced QTimer polling with efficient real-time event hooks
            events.subscribe("request_succeeded", lambda resp: self.signals.usage_updated.emit())
            events.subscribe("request_failed", lambda err, ctx: self.signals.usage_updated.emit())

    @Slot()
    def _update_display(self):
        if not self.container: return
        analytics = self.container.get_service("usage_analytics")
        if not analytics: return
        
        stats = analytics.get_global_analytics()
        if not stats: return
        
        self.lbl_reqs.setText(str(stats.total_requests))
        self.lbl_success.setText(f"{stats.success_rate:.1f}%")
        self.lbl_tokens.setText(f"{stats.total_tokens:,}")
        self.lbl_cost.setText(f"${stats.total_cost:.4f}")