# gui/compliance/compliance_dashboard.py
from typing import Any

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal

from gui.compliance.upload_readiness_widget import UploadReadinessWidget
from gui.compliance.warning_panel import WarningPanelWidget
from gui.compliance.recommendation_panel import RecommendationPanelWidget
from gui.compliance.marketplace_selector import MarketplaceSelectorWidget

class ComplianceDashboardWidget(QWidget):
    run_check_requested = Signal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_marketplace = "adobe_stock"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        self.selector = MarketplaceSelectorWidget()
        self.selector.marketplace_changed.connect(self._on_marketplace_changed)
        
        self.btn_check = QPushButton("Run Compliance Check")
        self.btn_check.clicked.connect(lambda: self.run_check_requested.emit(self.current_marketplace))
        self.btn_check.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 5px 15px;")
        
        top_layout.addWidget(self.selector)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_check)
        layout.addLayout(top_layout)

        self.readiness_widget = UploadReadinessWidget()
        layout.addWidget(self.readiness_widget)

        panels_layout = QHBoxLayout()
        self.warning_panel = WarningPanelWidget()
        self.rec_panel = RecommendationPanelWidget()
        
        panels_layout.addWidget(self.warning_panel, stretch=1)
        panels_layout.addWidget(self.rec_panel, stretch=1)
        
        layout.addLayout(panels_layout)

    def _on_marketplace_changed(self, mkp_key: str):
        self.current_marketplace = mkp_key

    def update_dashboard(self, report: Any):
        self.readiness_widget.update_status(report.status, report.scores.overall)
        self.warning_panel.update_warnings(report.critical_errors + report.warnings)
        self.rec_panel.update_recommendations(report.recommendations)
