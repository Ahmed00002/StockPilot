# gui/integration/pipeline_dashboard.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget
from PySide6.QtCore import QObject, Signal, Slot

from gui.integration.health_dashboard import HealthDashboardWidget
from gui.integration.performance_monitor import PerformanceMonitorWidget
from gui.integration.diagnostics_panel import DiagnosticsPanel

# INTEGRATION FIX: Moved inline import to module level
from integration.pipeline_health_monitor import HealthStatus

class PipelineSignals(QObject):
    """Thread-safe signal proxy for background pipeline diagnostic events."""
    diagnostics_updated = Signal(dict)

class PipelineDashboardWidget(QWidget):
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.signals = PipelineSignals()
        self._init_ui()
        self._connect_events()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        self.tab_health = QWidget()
        health_layout = QHBoxLayout(self.tab_health)
        
        self.health_widget = HealthDashboardWidget()
        self.perf_widget = PerformanceMonitorWidget()
        
        health_layout.addWidget(self.health_widget, stretch=1)
        health_layout.addWidget(self.perf_widget, stretch=1)
        
        self.diag_panel = DiagnosticsPanel()
        
        self.tabs.addTab(self.tab_health, "Health & Performance")
        self.tabs.addTab(self.diag_panel, "Advanced Diagnostics")
        
        layout.addWidget(self.tabs)

    def _connect_events(self):
        self.signals.diagnostics_updated.connect(self._on_diagnostics_ui)
        
        if not self.container: return
        
        integration_mgr = self.container.get_service("integration_manager")
        if integration_mgr and hasattr(integration_mgr, 'events'):
            # INTEGRATION FIX: Bridge background events back to main UI thread safely
            integration_mgr.events.subscribe("diagnostics_ready", lambda data: self.signals.diagnostics_updated.emit(data))

    @Slot(dict)
    def _on_diagnostics_ui(self, diag_report: dict):
        self.update_from_diagnostics(diag_report)

    def update_from_diagnostics(self, diag_report: dict):
        if 'health_checks' in diag_report:
            statuses = {k: HealthStatus(is_healthy=v['healthy'], component=k, message=v['message']) for k,v in diag_report['health_checks'].items()}
            self.health_widget.update_health(statuses)
            
        if 'performance_averages' in diag_report:
            self.perf_widget.update_performance(diag_report['performance_averages'])
            
        self.diag_panel.update_diagnostics(diag_report)