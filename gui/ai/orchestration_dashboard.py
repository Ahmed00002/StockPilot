# gui/ai/orchestration_dashboard.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QProgressBar
from PySide6.QtCore import Qt, Slot, QObject, Signal
import logging

logger = logging.getLogger("OrchestrationDashboard")

class OrchestrationSignals(QObject):
    """Proxy object to safely bridge background execution events to the Main UI Thread."""
    request_started = Signal(object, object)
    request_ended = Signal(object)
    request_error = Signal(object, object)
    provider_selected = Signal(str, object)
    failover_triggered = Signal(str, object)

class OrchestrationDashboard(QWidget):
    """Real-time UI visualization of the active routing and execution pipelines."""

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        # INTEGRATION FIX: Standardized DI container approach
        self.container = container
        
        self.active_requests = 0
        self.failover_count = 0
        
        self.signals = OrchestrationSignals()
        self._setup_ui()
        self._connect_events()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Pipeline State
        pipeline_group = QGroupBox("Execution Pipeline State")
        p_layout = QVBoxLayout()
        
        self.lbl_active = QLabel("Active Requests: 0")
        self.lbl_failovers = QLabel("Failover Events: 0")
        self.lbl_last_provider = QLabel("Last Routed: None")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0) # Indeterminate initially
        self.progress_bar.hide()
        
        p_layout.addWidget(self.lbl_active)
        p_layout.addWidget(self.lbl_failovers)
        p_layout.addWidget(self.lbl_last_provider)
        p_layout.addWidget(self.progress_bar)
        
        pipeline_group.setLayout(p_layout)
        layout.addWidget(pipeline_group)
        layout.addStretch()

    def _connect_events(self):
        # Bind Qt signals to the UI update slots
        self.signals.request_started.connect(self._on_request_start_ui)
        self.signals.request_ended.connect(self._on_request_end_ui)
        self.signals.request_error.connect(self._on_request_error_ui)
        self.signals.provider_selected.connect(self._on_provider_select_ui)
        self.signals.failover_triggered.connect(self._on_failover_ui)

        if not self.container: return
        events = self.container.get_service("orchestration_events")
        if events:
            # INTEGRATION FIX: Safely route background Python events to thread-safe Qt Signals
            events.subscribe("request_received", lambda req, ctx: self.signals.request_started.emit(req, ctx))
            events.subscribe("request_succeeded", lambda resp: self.signals.request_ended.emit(resp))
            events.subscribe("request_failed", lambda err, ctx: self.signals.request_error.emit(err, ctx))
            events.subscribe("provider_selected", lambda prov, req: self.signals.provider_selected.emit(prov, req))
            events.subscribe("failover_triggered", lambda prov, err: self.signals.failover_triggered.emit(prov, err))

    @Slot(object, object)
    def _on_request_start_ui(self, req, ctx):
        self.active_requests += 1
        self._update_ui()

    @Slot(object)
    def _on_request_end_ui(self, resp):
        self.active_requests = max(0, self.active_requests - 1)
        self._update_ui()

    @Slot(object, object)
    def _on_request_error_ui(self, err, ctx):
        self.active_requests = max(0, self.active_requests - 1)
        self._update_ui()

    @Slot(str, object)
    def _on_provider_select_ui(self, provider, req):
        self.lbl_last_provider.setText(f"Last Routed: {provider}")

    @Slot(str, object)
    def _on_failover_ui(self, provider, err):
        self.failover_count += 1
        self._update_ui()

    def _update_ui(self):
        self.lbl_active.setText(f"Active Requests: {self.active_requests}")
        self.lbl_failovers.setText(f"Failover Events: {self.failover_count}")
        if self.active_requests > 0:
            self.progress_bar.show()
        else:
            self.progress_bar.hide()