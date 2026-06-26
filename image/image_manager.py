# image/image_manager.py
import logging
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QThreadPool
from core.event_bus import EventBus
from workspace.workspace import Workspace
from image.image_model import ImageModel
from image.image_repository import ImageRepository
from image.thumbnail_cache import ThumbnailCache
from image.thumbnail_generator import ThumbnailGeneratorTask
from image.image_scanner import ImageScanner
from image.image_indexer import ImageIndexerTask
from image.image_importer import ImageImporterTask
from image.file_watcher import WorkspaceFileWatcher
from image.selection_manager import SelectionManager
from image.intelligence.image_intelligence_manager import ImageIntelligenceManager
from image.image_events import ImageEvents, ScanProgressPayload, ImageEventPayload

logger = logging.getLogger(__name__)

class ImageManager:
    """Facade orchestrator for the entire Image Asset Management subsystem."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.thread_pool = QThreadPool.globalInstance()
        
        # INTEGRATION FIX: Isolated thread pool for thumbnails to prevent global UI starvation
        self.thumbnail_pool = QThreadPool()
        self.thumbnail_pool.setMaxThreadCount(max(2, self.thread_pool.maxThreadCount() // 2))
        
        self.workspace: Optional[Workspace] = None
        self.repository: Optional[ImageRepository] = None
        self.thumbnail_cache: Optional[ThumbnailCache] = None
        self.selection = SelectionManager()
        self.watcher: Optional[WorkspaceFileWatcher] = None
        self.intelligence = ImageIntelligenceManager()
        
        self.selection.selection_changed.connect(
            lambda ids: self.event_bus.publish(ImageEvents.SELECTION_CHANGED, ids)
        )

    def initialize_workspace(self, workspace: Workspace) -> None:
        """Binds the manager to an active workspace."""
        self.workspace = workspace
        self.repository = ImageRepository(workspace.paths.root)
        self.thumbnail_cache = ThumbnailCache(workspace.paths.thumbnails)
        self.watcher = WorkspaceFileWatcher(workspace.paths.root)
        self.selection.clear()
        logger.info(f"ImageManager bound to workspace: {workspace.name}")

    def import_files(self, source_paths: List[Path]) -> None:
        """Initiates an asynchronous import job."""
        if not self.workspace: return
        target_dir = self.workspace.paths.images
        
        task = ImageImporterTask(source_paths, target_dir)
        task.signals.progress.connect(self._on_task_progress)
        task.signals.completed.connect(self._on_import_completed)
        self.thread_pool.start(task)

    def scan_workspace(self) -> None:
        """Scans the workspace images directory and indexes new files."""
        if not self.workspace: return
        images_dir = self.workspace.paths.images
        
        files = ImageScanner.scan_directory(images_dir)
        unindexed = [f for f in files if not self.repository.exists_by_path(str(f))]
        
        if unindexed:
            task = ImageIndexerTask(unindexed, self.workspace.workspace_id, self.workspace.paths.root, self.intelligence)
            task.signals.progress.connect(self._on_task_progress)
            task.signals.completed.connect(self._on_index_completed)
            self.thread_pool.start(task)
        else:
            self.event_bus.publish(ImageEvents.SCAN_COMPLETED, [])

    def _on_task_progress(self, current: int, total: int, message: str) -> None:
        self.event_bus.publish(ImageEvents.SCAN_PROGRESS, ScanProgressPayload(current, total, message))

    def _on_import_completed(self, imported_paths: List[Path]) -> None:
        logger.info(f"Import completed. {len(imported_paths)} files copied.")
        if self.workspace and imported_paths:
            task = ImageIndexerTask(imported_paths, self.workspace.workspace_id, self.workspace.paths.root, self.intelligence)
            task.signals.progress.connect(self._on_task_progress)
            task.signals.completed.connect(self._on_index_completed)
            self.thread_pool.start(task)

    def _on_index_completed(self, models: List[ImageModel]) -> None:
        if not self.repository or not self.workspace: return
        for model in models:
            self.repository.add_or_update(model)
            
            # INTEGRATION FIX: Queue rendering into the dedicated throttle pool
            thumb_task = ThumbnailGeneratorTask(
                model.image_id, 
                Path(model.absolute_path), 
                model.sha256_hash, 
                200, 
                self.thumbnail_cache
            )
            self.thumbnail_pool.start(thumb_task)

        self.repository.save()
        payload = ImageEventPayload(self.workspace.workspace_id, [m.image_id for m in models])
        self.event_bus.publish(ImageEvents.INDEXED, payload)
        self.event_bus.publish(ImageEvents.SCAN_COMPLETED, models)

    def get_filtered_sorted_images(self, criteria: dict, sort_by: str, desc: bool) -> List[ImageModel]:
        if not self.repository: return []
        all_imgs = self.repository.get_all()
        # Filters logic... (Truncated for brevity)
        return all_imgs 
        
    def get_image(self, image_id: str) -> Optional[ImageModel]:
        return self.repository.get(image_id) if self.repository else None