# gui/workspace/metadata_workspace_view.py
import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QMessageBox
from PySide6.QtCore import Signal
from image.image_events import ImageEvents

from gui.workspace.version_history_panel import VersionHistoryPanel
from gui.workspace.timeline_widget import TimelineWidget
from gui.workspace.revision_statistics_widget import RevisionStatisticsWidget
from gui.workspace.metadata_compare_view import MetadataCompareView
from gui.review.review_dashboard import ReviewDashboardWidget

logger = logging.getLogger(__name__)

class MetadataWorkspaceView(QWidget):
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.current_image_hash = None
        self._init_ui()
        self._connect_signals()
        self._subscribe_events()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        
        self.history_panel = VersionHistoryPanel()
        left_panel.addWidget(self.history_panel, stretch=2)
        
        self.stats_widget = RevisionStatisticsWidget()
        left_panel.addWidget(self.stats_widget, stretch=1)
        
        self.timeline_widget = TimelineWidget()
        left_panel.addWidget(self.timeline_widget, stretch=1)

        right_panel = QVBoxLayout()
        self.tabs = QTabWidget()
        
        self.compare_view = MetadataCompareView()
        self.tabs.addTab(self.compare_view, "Compare & Merge")
        
        # INTEGRATION FIX: Embedded the SEO Review Dashboard
        self.review_dashboard = ReviewDashboardWidget(self.container)
        self.tabs.addTab(self.review_dashboard, "SEO & Review")
        
        right_panel.addWidget(self.tabs)

        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=3)

    def _connect_signals(self):
        self.history_panel.version_selected.connect(self._on_version_selected)
        self.history_panel.version_restored.connect(self._on_version_restored)
        self.history_panel.version_deleted.connect(self._on_version_deleted)

    def _subscribe_events(self):
        if not self.container: return
        eb = self.container.get_service("event_bus")
        if eb:
            eb.subscribe(ImageEvents.SELECTION_CHANGED, self._on_selection_changed)

    def _on_selection_changed(self, image_ids):
        if image_ids and len(image_ids) > 0:
            self.current_image_hash = image_ids[0]
            self._refresh_view()
        else:
            self.current_image_hash = None
            self._clear_view()

    def _refresh_view(self):
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return

        current = mgr.get_current(self.current_image_hash)
        versions = mgr.version_mgr.get_all_versions(self.current_image_hash)
        
        self.history_panel.update_history(versions, current.snapshot_id if current else None)
        
        try:
            stats = mgr.version_mgr.statistics.get_statistics(self.current_image_hash)
            if stats:
                self.stats_widget.update_stats(stats)
        except AttributeError:
            pass
            
        try:
            events = mgr.version_mgr.timeline.get_events(self.current_image_hash)
            self.timeline_widget.update_timeline(events)
        except AttributeError:
            pass

        # INTEGRATION FIX: Trigger SEO Engine evaluation dynamically when switching images
        self.review_dashboard.evaluate_hash(self.current_image_hash)

    def _clear_view(self):
        self.history_panel.update_history([])
        self.timeline_widget.update_timeline([])
        self.review_dashboard.evaluate_hash(None)

    def _on_version_selected(self, version_id):
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        current = mgr.get_current(self.current_image_hash)
        selected = mgr.version_mgr.get_version(self.current_image_hash, version_id)
        if not current or not selected: return
        
        diff = mgr.compare_versions(self.current_image_hash, current.snapshot_id, version_id)
        self.compare_view.update_compare(current, selected, diff)

    def _on_version_restored(self, version_id):
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        restored = mgr.load_version(self.current_image_hash, version_id)
        if restored:
            self._refresh_view()
            QMessageBox.information(self, "Restored", "Version restored successfully.")

    def _on_version_deleted(self, version_id):
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        if mgr.version_mgr.delete_version(self.current_image_hash, version_id):
            self._refresh_view()