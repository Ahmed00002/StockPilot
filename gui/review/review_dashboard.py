# gui/review/review_dashboard.py
import logging
from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

from metadata.review.review_models import MetadataPackage
from gui.review.quality_widget import QualityScoreWidget
from gui.review.recommendation_widget import RecommendationWidget

logger = logging.getLogger(__name__)

class ReviewDashboardWidget(QWidget):
    improve_requested = Signal()
    accept_requested = Signal()

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.current_report = None
        self.current_image_hash = None
        self._init_ui()
        self._connect_actions()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        title = QLabel("Metadata Intelligence Review")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.status_label = QLabel("Status: Pending")
        self.status_label.setStyleSheet("font-weight: bold; color: gray;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        layout.addLayout(header_layout)

        content_layout = QHBoxLayout()
        
        self.quality_widget = QualityScoreWidget()
        content_layout.addWidget(self.quality_widget, stretch=1)
        
        self.recommendation_widget = RecommendationWidget()
        content_layout.addWidget(self.recommendation_widget, stretch=2)
        
        layout.addLayout(content_layout)

        btn_layout = QHBoxLayout()
        self.btn_improve = QPushButton("Auto-Improve (AI Refinement)")
        
        self.btn_accept = QPushButton("Accept Metadata")
        self.btn_accept.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        
        btn_layout.addWidget(self.btn_improve)
        btn_layout.addWidget(self.btn_accept)
        layout.addLayout(btn_layout)

    def _connect_actions(self):
        self.btn_improve.clicked.connect(self.improve_requested.emit)
        self.btn_accept.clicked.connect(self.accept_requested.emit)
        
        # INTEGRATION FIX: Connect local signals to execution logic
        self.improve_requested.connect(self._on_improve)
        self.accept_requested.connect(self._on_accept)

    def evaluate_hash(self, image_hash: str):
        """Called externally to run the review pipeline."""
        self.current_image_hash = image_hash
        if not self.container or not image_hash:
            self.update_dashboard(None)
            return
            
        mgr = self.container.get_service("metadata_workspace_manager")
        engine = self.container.get_service("metadata_review_engine")
        
        if not mgr or not engine: 
            self.update_dashboard(None)
            return
            
        current = mgr.get_current(image_hash)
        if current:
            # INTEGRATION FIX: Build package for review engine
            package = MetadataPackage(
                title=current.title,
                description=current.description,
                keywords=current.keywords
            )
            report = engine.review(package)
            self.update_dashboard(report)
        else:
            self.update_dashboard(None)

    def update_dashboard(self, report: Any):
        self.current_report = report
        
        if not report:
            self.status_label.setText("Status: NO METADATA")
            self.status_label.setStyleSheet("font-weight: bold; color: gray;")
            self.btn_improve.setEnabled(False)
            self.btn_accept.setEnabled(False)
            return

        self.btn_accept.setEnabled(True)
        self.quality_widget.update_scores(report)
        self.recommendation_widget.update_recommendations(report)
        
        if report.is_approved:
            self.status_label.setText("Status: PASSED")
            self.status_label.setStyleSheet("font-weight: bold; color: #28a745;")
        else:
            self.status_label.setText("Status: NEEDS IMPROVEMENT")
            self.status_label.setStyleSheet("font-weight: bold; color: #dc3545;")
            
        self.btn_improve.setEnabled(report.revision_count == 0 and not report.is_approved)

    def _on_improve(self):
        if not self.container or not self.current_report or not self.current_image_hash: return
        engine = self.container.get_service("metadata_review_engine")
        mgr = self.container.get_service("metadata_workspace_manager")
        if not engine or not mgr: return
        
        logger.info(f"Triggering Auto-Improve for {self.current_image_hash}")
        new_report = engine.request_improvement(self.current_report)
        
        if new_report and hasattr(new_report, 'improved_package') and new_report.improved_package:
            pkg = new_report.improved_package
            mgr.save_current(
                image_hash=self.current_image_hash,
                title=pkg.title,
                description=pkg.description,
                keywords=pkg.keywords,
                provider="AI Auto-Improve",
                reason="Auto-Improvement applied"
            )
            self.update_dashboard(new_report)

    def _on_accept(self):
        if not self.container or not self.current_image_hash or not self.current_report: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if mgr:
            current = mgr.get_current(self.current_image_hash)
            if current:
                mgr.save_current(
                    image_hash=self.current_image_hash,
                    title=current.title,
                    description=current.description,
                    keywords=current.keywords,
                    provider=current.provider,
                    reason="User Approved"
                )
                logger.info(f"Metadata Approved for {self.current_image_hash}")