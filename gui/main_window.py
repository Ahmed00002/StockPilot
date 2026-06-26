# gui/main_window.py
import logging
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QStatusBar, QToolBar, QMenuBar, 
    QMenu, QStackedWidget, QLabel, QFrame, QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt, QSize

from core.constants import AppConstants
from gui.widgets.icon_loader import IconLoader
from gui.navigation.sidebar import Sidebar
from gui.navigation.breadcrumb import BreadcrumbWidget
from gui.navigation.search_box import SearchBox
from gui.navigation.navigation_manager import NavigationManager
from gui.navigation.command_palette import CommandPalette

# Pages
from gui.pages.welcome_page import WelcomePage
from gui.pages.dashboard_page import DashboardPage
from gui.pages.history_page import HistoryPage
from gui.pages.settings_page import SettingsPage
from gui.pages.plugin_page import PluginPage
from gui.pages.about_page import AboutPage
from gui.workspaces.workspace_home import WorkspaceHomePage
from gui.pages.images_page import ImagesPage
from image.image_events import ImageEvents

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """The central application window acting as the root layout orchestrator."""
    
    def __init__(self, container=None) -> None:
        super().__init__()
        self.container = container 
        
        self.setWindowTitle(f"{AppConstants.APP_NAME} - v{AppConstants.APP_VERSION}")
        self.setMinimumSize(1024, 600)
        
        self._ui_config_path = AppConstants.CONFIG_DIR / "ui_config.json"
        
        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()
        self._setup_navigation()
        self._register_shortcuts()
        self._restore_window_state()
        
        self.command_palette = CommandPalette(self)
        self.command_palette.command_selected.connect(self._handle_command_palette_command)
        self._subscribe_events()
        
        logger.info("Main Window initialized.")

    def _init_ui(self) -> None:
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setObjectName("MainSplitter")
        
        self.left_sidebar = Sidebar(self)
        
        workspace_container = QWidget()
        workspace_layout = QVBoxLayout(workspace_container)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        
        self.breadcrumb_bar = QFrame()
        self.breadcrumb_bar.setFixedHeight(30)
        self.breadcrumb_bar.setStyleSheet("background-color: #252526; border-bottom: 1px solid #3f3f46;")
        breadcrumb_layout = QHBoxLayout(self.breadcrumb_bar)
        breadcrumb_layout.setContentsMargins(16, 0, 16, 0)
        self.breadcrumb = BreadcrumbWidget()
        breadcrumb_layout.addWidget(self.breadcrumb)
        
        self.workspace_stack = QStackedWidget()
        self.workspace_stack.setObjectName("CentralWorkspace")
        
        workspace_layout.addWidget(self.breadcrumb_bar)
        workspace_layout.addWidget(self.workspace_stack)
        
        self.right_inspector = QFrame()
        self.right_inspector.setObjectName("RightInspector")
        self.right_inspector.setMinimumWidth(250)
        inspector_layout = QVBoxLayout(self.right_inspector)
        inspector_layout.addWidget(QLabel("Properties Inspector (Pending)"))
        self.right_inspector.hide() 
        
        self.main_splitter.addWidget(self.left_sidebar)
        self.main_splitter.addWidget(workspace_container)
        self.main_splitter.addWidget(self.right_inspector)
        
        self.main_splitter.setSizes([240, 1040, 0])
        self.main_splitter.setCollapsible(0, True)
        self.main_splitter.setCollapsible(1, False)
        
        self.main_layout.addWidget(self.main_splitter)

    def _create_placeholder(self, module_name: str) -> QWidget:
        placeholder = QWidget()
        layout = QVBoxLayout(placeholder)
        lbl = QLabel(f"Module '{module_name}' Pending Implementation")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #858585; font-size: 16px;")
        layout.addWidget(lbl)
        return placeholder

    def _setup_navigation(self) -> None:
        self.nav_manager = NavigationManager(self.workspace_stack, self.left_sidebar, self.breadcrumb)
        
        def safe_register(page_id: str, page_class, title: str) -> None:
            try:
                page_instance = page_class(self.container, parent=self) if self.container else page_class(parent=self)
                if hasattr(page_instance, "action_requested"):
                    page_instance.action_requested.connect(self.nav_manager.navigate)
                self.nav_manager.register_page(page_id, page_instance, title)
            except Exception as e:
                logger.error(f"Failed to load page '{page_id}': {e}", exc_info=True)
                self.nav_manager.register_page(page_id, self._create_placeholder(f"{title} (Load Error)"), title)

        safe_register("welcome", WelcomePage, "Welcome")
        safe_register("dashboard", DashboardPage, "Dashboard")
        safe_register("history", HistoryPage, "History")
        safe_register("settings", SettingsPage, "Settings")
        safe_register("plugins", PluginPage, "Plugins")
        safe_register("help", AboutPage, "Help")
        safe_register("workspaces", WorkspaceHomePage, "Workspaces")
        safe_register("images", ImagesPage, "Images")
        
        missing_modules = [
            ("metadata", "Metadata Studio"),
            ("ai_studio", "AI Studio"), ("seo", "SEO Engine"),
            ("export", "Export Center"), ("analytics", "Analytics"),
            ("logs", "Logs")
        ]
        
        for pid, title in missing_modules:
            self.nav_manager.register_page(pid, self._create_placeholder(title), title)
        
        self.nav_manager.page_changed.connect(self._on_page_changed)
        self.nav_manager.navigate("welcome")

    def _on_page_changed(self, page_id: str) -> None:
        self.lbl_status.setText(f"Active Page: {page_id}")

    def _create_actions(self) -> None:
        self.act_new_workspace = QAction(IconLoader.get_icon("plus"), "New Workspace", self)
        self.act_new_workspace.triggered.connect(lambda: self.nav_manager.navigate("workspaces"))
        
        self.act_open = QAction(IconLoader.get_icon("folder-open"), "Open Workspace...", self)
        self.act_open.triggered.connect(self._open_workspace_action)
        
        self.act_close_workspace = QAction(IconLoader.get_icon("x"), "Close Workspace", self)
        self.act_close_workspace.triggered.connect(self._close_workspace_action)
        
        self.act_import = QAction(IconLoader.get_icon("import"), "Import Images...", self)
        self.act_import.triggered.connect(self._import_images_action)
        
        self.act_save = QAction(IconLoader.get_icon("save"), "Save Project State", self)
        self.act_export = QAction(IconLoader.get_icon("export"), "Export Data...", self)
        
        self.act_history = QAction(IconLoader.get_icon("history"), "History", self)
        self.act_history.triggered.connect(lambda: self.nav_manager.navigate("history"))
        
        self.act_settings = QAction(IconLoader.get_icon("settings"), "Settings", self)
        self.act_settings.triggered.connect(lambda: self.nav_manager.navigate("settings"))
        
        self.act_fullscreen = QAction("Toggle Fullscreen", self)
        self.act_fullscreen.triggered.connect(self._toggle_fullscreen)
        
        self.act_exit = QAction("Exit", self)
        self.act_exit.triggered.connect(self.close)
        
        self.act_toggle_sidebar = QAction(IconLoader.get_icon("menu"), "Toggle Sidebar", self)
        self.act_toggle_sidebar.triggered.connect(self._toggle_sidebar)
        
        self.act_command_palette = QAction("Command Palette", self)
        self.act_command_palette.triggered.connect(self._show_command_palette)

    def _import_images_action(self) -> None:
        if not self.container: return
        wm = self.container.get_service("workspace_manager")
        if not wm or not wm.active_workspace:
            QMessageBox.warning(self, "No Workspace", "Please open or create a workspace before importing images.")
            return
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Images", "", "Image Files (*.png *.jpg *.jpeg *.webp *.tiff *.bmp)"
        )
        if files:
            im = self.container.get_service("image_manager")
            if im:
                im.import_files([Path(f) for f in files])
                self.nav_manager.navigate("images")

    def _open_workspace_action(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Workspace Directory")
        if folder and self.container:
            wm = self.container.get_service("workspace_manager")
            if wm:
                if not wm.load_workspace(folder):
                    QMessageBox.critical(self, "Error", f"Failed to load workspace at {folder}")

    def _close_workspace_action(self) -> None:
        if self.container:
            wm = self.container.get_service("workspace_manager")
            if wm and wm.active_workspace:
                wm.close_workspace()
                QMessageBox.information(self, "Closed", "Workspace closed successfully.")

    def _toggle_sidebar(self) -> None:
        self.left_sidebar.toggle_collapse()

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _show_command_palette(self) -> None:
        parent_rect = self.geometry()
        x = parent_rect.x() + (parent_rect.width() - self.command_palette.width()) // 2
        y = parent_rect.y() + (parent_rect.height() - self.command_palette.height()) // 3
        self.command_palette.move(x, y)
        self.command_palette.exec()

    def _handle_command_palette_command(self, command: str) -> None:
        command_routes = {
            "Export: Generate Adobe CSV": "export",
            "Metadata: Auto Generate All": "metadata",
            "Workspace: Open Settings": "settings",
        }

        if command == "View: Toggle Fullscreen":
            self._toggle_fullscreen()
            return

        if command == "Theme: Switch to Light Mode":
            if self.container:
                theme_manager = self.container.get_service("theme_manager")
                if theme_manager and hasattr(theme_manager, "apply_theme"):
                    theme_manager.apply_theme("light")
            return

        page_id = command_routes.get(command)
        if page_id:
            self.nav_manager.navigate(page_id)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.act_new_workspace)
        file_menu.addAction(self.act_open)
        file_menu.addAction(self.act_close_workspace)
        file_menu.addSeparator()
        file_menu.addAction(self.act_import)
        file_menu.addAction(self.act_save)
        file_menu.addAction(self.act_export)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)
        
        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self.act_toggle_sidebar)
        view_menu.addAction(self.act_fullscreen)
        view_menu.addSeparator()
        view_menu.addAction(self.act_command_palette)
        
        menu_bar.addMenu("&Help")

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        toolbar.addAction(self.act_toggle_sidebar)
        toolbar.addSeparator()
        toolbar.addAction(self.act_new_workspace)
        toolbar.addAction(self.act_open)
        toolbar.addAction(self.act_save)
        
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Preferred)
        toolbar.addWidget(spacer)
        
        self.search_box = SearchBox()
        toolbar.addWidget(self.search_box)
        
        toolbar.addSeparator()
        toolbar.addAction(self.act_settings)

    def _create_status_bar(self) -> None:
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.lbl_status = QLabel("Ready")
        self.lbl_workspace = QLabel("Workspace: None")
        self.lbl_provider = QLabel("Provider: None")
        self.lbl_queue = QLabel("Images: 0")
        self.lbl_version = QLabel(f"v{AppConstants.APP_VERSION}")
        status_bar.addWidget(self.lbl_status, 1)
        status_bar.addPermanentWidget(self.lbl_workspace)
        status_bar.addPermanentWidget(self.lbl_provider)
        status_bar.addPermanentWidget(self.lbl_queue)
        status_bar.addPermanentWidget(self.lbl_version)

    def _subscribe_events(self) -> None:
        if self.container:
            eb = self.container.get_service("event_bus")
            if eb:
                eb.subscribe(AppConstants.EVENT_WORKSPACE_LOADED, self._on_status_workspace_update)
                eb.subscribe(ImageEvents.INDEXED, self._update_image_count)
                eb.subscribe(ImageEvents.SCAN_COMPLETED, self._update_image_count)

    def _on_status_workspace_update(self, workspace_name=None) -> None:
        if workspace_name:
            self.lbl_workspace.setText(f"Workspace: {workspace_name}")
            self._update_image_count()
        else:
            self.lbl_workspace.setText("Workspace: None")
            self.lbl_queue.setText("Images: 0")

    def _update_image_count(self, payload=None) -> None:
        if self.container:
            im = self.container.get_service("image_manager")
            if im and im.repository:
                count = len(im.repository.get_all())
                self.lbl_queue.setText(f"Images: {count}")

    def _register_shortcuts(self) -> None:
        self.act_open.setShortcut(QKeySequence("Ctrl+O"))
        self.act_save.setShortcut(QKeySequence("Ctrl+S"))
        self.act_settings.setShortcut(QKeySequence("Ctrl+,"))
        self.act_fullscreen.setShortcut(QKeySequence("F11"))
        self.act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.act_command_palette.setShortcut(QKeySequence("Ctrl+Shift+P"))

    def _restore_window_state(self) -> None:
        if not self._ui_config_path.exists(): return
        try:
            with open(self._ui_config_path, 'r', encoding='utf-8') as f: config = json.load(f)
            w_cfg = config.get("window", {})
            self.setGeometry(w_cfg.get("x", 100), w_cfg.get("y", 100), w_cfg.get("width", 1280), w_cfg.get("height", 720))
            if w_cfg.get("maximized", False): self.showMaximized()
            
            sizes = w_cfg.get("splitter_sizes")
            if sizes and isinstance(sizes, list):
                self.main_splitter.setSizes(sizes)
        except Exception: pass

    def closeEvent(self, event) -> None:
        self._save_window_state()
        super().closeEvent(event)

    def _save_window_state(self) -> None:
        config = {}
        if self._ui_config_path.exists():
            try:
                with open(self._ui_config_path, 'r') as f: config = json.load(f)
            except Exception: pass
            
        config["window"] = {
            "width": self.width(), 
            "height": self.height(), 
            "x": self.x(), 
            "y": self.y(), 
            "maximized": self.isMaximized(),
            "splitter_sizes": self.main_splitter.sizes()
        }
        
        try:
            self._ui_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ui_config_path, 'w') as f: 
                json.dump(config, f, indent=4)
        except Exception as e: 
            logger.warning(f"Failed to save window state: {e}")
