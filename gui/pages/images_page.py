# gui/pages/images_page.py
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QFileDialog, QMessageBox, QDialog
)
from PySide6.QtCore import Qt, QItemSelectionModel, Signal
from gui.images.image_toolbar import ImageToolbar
from gui.images.image_grid import ImageGrid, ImageListModel
from gui.images.image_preview import ImagePreviewWidget
from gui.images.image_properties_panel import ImagePropertiesPanel
from gui.images.import_dialog import ImportDialog
from image.image_events import ImageEvents
from core.constants import AppConstants

logger = logging.getLogger(__name__)

class ImagesPage(QWidget):
    """The primary interface for managing, viewing, and filtering workspace images."""
    
    # INTEGRATION FIX: Added standard navigation routing signal
    action_requested = Signal(str)
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        self.setObjectName("ImagesPage")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.toolbar = ImageToolbar(self)
        self.layout.addWidget(self.toolbar)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        grid_container = QWidget()
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid = ImageGrid(self)
        self.model = ImageListModel()
        self.grid.setModel(self.model)
        grid_layout.addWidget(self.grid)
        
        self.right_panel = QSplitter(Qt.Orientation.Vertical)
        
        self.preview = ImagePreviewWidget(self)
        self.properties = ImagePropertiesPanel(self)
        
        self.right_panel.addWidget(self.preview)
        self.right_panel.addWidget(self.properties)
        self.right_panel.setSizes([400, 400])
        
        self.splitter.addWidget(grid_container)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([800, 300])
        self.splitter.setCollapsible(0, False)
        
        self.layout.addWidget(self.splitter)
        self._connect_events()

    def _connect_events(self) -> None:
        self.toolbar.btn_import.clicked.connect(self._on_import_clicked)
        self.toolbar.slider_zoom.valueChanged.connect(self.grid.set_zoom_level)
        self.toolbar.cmb_sort.currentTextChanged.connect(lambda _: self.refresh_grid())
        
        sel_model = self.grid.selectionModel()
        if sel_model:
            sel_model.selectionChanged.connect(self._on_selection_changed)
            
        # INTEGRATION FIX: Direct navigation to Metadata Studio upon double-click
        self.grid.doubleClicked.connect(lambda idx: self.action_requested.emit("metadata_studio"))
            
        if self.container:
            eb = self.container.get_service("event_bus")
            if eb:
                eb.subscribe(ImageEvents.SCAN_COMPLETED, self._on_scan_completed)
                eb.subscribe(ImageEvents.INDEXED, self._on_indexed)
                eb.subscribe(AppConstants.EVENT_WORKSPACE_LOADED, self._on_workspace_loaded)
                eb.subscribe(ImageEvents.SELECTION_CHANGED, self._on_external_selection)

    def _on_import_clicked(self) -> None:
        if not self.container: return
        wm = self.container.get_service("workspace_manager")
        if not wm or not wm.active_workspace:
            QMessageBox.warning(self, "No Workspace", "Please open or create a workspace before importing images.")
            return
            
        dialog = ImportDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            paths = dialog.get_paths()
            if paths:
                im = self.container.get_service("image_manager")
                if im:
                    im.import_files([Path(p) for p in paths])

    def _on_selection_changed(self, selected, deselected) -> None:
        indexes = self.grid.selectionModel().selectedIndexes()
        
        if not indexes:
            self.preview.set_image(None)
            self.properties.set_model(None)
            if self.container:
                im = self.container.get_service("image_manager")
                if im:
                    im.selection.set_selection([])
            return

        if self.container:
            model_item = self.model.data(indexes[0], Qt.ItemDataRole.UserRole)
            if model_item:
                self.preview.set_image(model_item)
                self.properties.set_model(model_item)
                
                im = self.container.get_service("image_manager")
                if im:
                    im.selection.set_selection([model_item.image_id])

    def _on_external_selection(self, payload=None) -> None:
        image_ids = payload if isinstance(payload, list) else []
        current_indexes = self.grid.selectionModel().selectedIndexes()
        current_ids = [self.model.data(idx, Qt.ItemDataRole.UserRole).image_id for idx in current_indexes if idx.isValid()]
        
        if set(current_ids) == set(image_ids): 
            return

        sel_model = self.grid.selectionModel()
        sel_model.blockSignals(True)
        sel_model.clearSelection()

        for row, img_model in enumerate(self.model.images):
            if img_model.image_id in image_ids:
                idx = self.model.index(row)
                sel_model.select(idx, QItemSelectionModel.SelectionFlag.Select)
                
        sel_model.blockSignals(False)
        
        if not image_ids:
            self.preview.set_image(None)
            self.properties.set_model(None)

    def _on_workspace_loaded(self, payload=None) -> None:
        if self.container:
            im = self.container.get_service("image_manager")
            wm = self.container.get_service("workspace_manager")
            if im and wm and wm.active_workspace:
                im.initialize_workspace(wm.active_workspace)
                im.scan_workspace()
        self.refresh_grid()

    def _on_scan_completed(self, payload=None) -> None:
        self.refresh_grid()

    def _on_indexed(self, payload=None) -> None:
        self.refresh_grid()

    def refresh_grid(self) -> None:
        if not self.container: return
        im = self.container.get_service("image_manager")
        if not im: return
        
        sort_by = self.toolbar.cmb_sort.currentText().lower().replace(" ", "_")
        images = im.get_filtered_sorted_images({}, sort_by, False)
        self.model.update_data(images)