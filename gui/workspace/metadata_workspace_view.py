# gui/workspace/metadata_workspace_view.py
import logging
from typing import Optional, List, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QMessageBox
from image.image_events import ImageEvents

from gui.workspace.version_history_panel import VersionHistoryPanel
from gui.workspace.timeline_widget import TimelineWidget
from gui.workspace.revision_statistics_widget import RevisionStatisticsWidget
from gui.workspace.metadata_compare_view import MetadataCompareView
from gui.review.review_dashboard import ReviewDashboardWidget

logger = logging.getLogger(__name__)

class MetadataWorkspaceView(QWidget):
    def __init__(self, container: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.container = container
        self.current_image_hash: Optional[str] = None
        self._init_ui()
        self._connect_signals()
        self._subscribe_events()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)

        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 0, 0)
        
        self.history_panel = VersionHistoryPanel()
        left_panel.addWidget(self.history_panel, stretch=2)
        
        self.stats_widget = RevisionStatisticsWidget()
        left_panel.addWidget(self.stats_widget, stretch=1)
        
        self.timeline_widget = TimelineWidget()
        left_panel.addWidget(self.timeline_widget, stretch=1)

        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        self.compare_view = MetadataCompareView()
        self.tabs.addTab(self.compare_view, "Compare & Merge")
        
        self.review_dashboard = ReviewDashboardWidget(self.container)
        self.tabs.addTab(self.review_dashboard, "SEO & Review")
        
        right_panel.addWidget(self.tabs)

        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=3)

    def _connect_signals(self) -> None:
        self.history_panel.version_selected.connect(self._on_version_selected)
        self.history_panel.version_restored.connect(self._on_version_restored)
        self.history_panel.version_deleted.connect(self._on_version_deleted)

    def _subscribe_events(self) -> None:
        if not self.container: return
        eb = self.container.get_service("event_bus")
        if eb:
            eb.subscribe(ImageEvents.SELECTION_CHANGED, self._on_selection_changed)

    def _on_selection_changed(self, image_ids: List[str]) -> None:
        if image_ids and len(image_ids) > 0:
            self.current_image_hash = image_ids[0]
            self._refresh_view()
        else:
            self.current_image_hash = None
            self._clear_view()

    def _refresh_view(self) -> None:
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return

        try:
            current = mgr.get_current(self.current_image_hash)
            versions = mgr.version_mgr.get_all_versions(self.current_image_hash)
            self.history_panel.update_history(versions, current.snapshot_id if current else None)
        except Exception as e:
            logger.error(f"Failed to update history: {e}")
            self.history_panel.update_history([])
        
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

        self.review_dashboard.evaluate_hash(self.current_image_hash)

    def _clear_view(self) -> None:
        self.history_panel.update_history([])
        self.timeline_widget.update_timeline([])
        self.review_dashboard.evaluate_hash(None)

    def _on_version_selected(self, version_id: str) -> None:
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        try:
            current = mgr.get_current(self.current_image_hash)
            selected = mgr.version_mgr.get_version(self.current_image_hash, version_id)
            if current and selected:
                diff = mgr.compare_versions(self.current_image_hash, current.snapshot_id, version_id)
                self.compare_view.update_compare(current, selected, diff)
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")

    def _on_version_restored(self, version_id: str) -> None:
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        reply = QMessageBox.question(
            self, "Confirm Restore",
            f"Restore version {version_id[:8]}?\nThis will create a new snapshot based on this version.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                restored = mgr.load_version(self.current_image_hash, version_id)
                if restored:
                    self._refresh_view()
                    QMessageBox.information(self, "Restored", f"Version {version_id[:8]} restored successfully.")
            except Exception as e:
                logger.error(f"Error restoring version: {e}")
                QMessageBox.critical(self, "Error", f"Failed to restore version:\n{e}")

    def _on_version_deleted(self, version_id: str) -> None:
        if not self.container or not self.current_image_hash: return
        mgr = self.container.get_service("metadata_workspace_manager")
        if not mgr: return
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Permanently delete version {version_id[:8]}?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if mgr.version_mgr.delete_version(self.current_image_hash, version_id):
                    self._refresh_view()
            except Exception as e:
                logger.error(f"Error deleting version: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete version:\n{e}")