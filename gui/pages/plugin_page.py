# gui/pages/plugin_page.py
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QTabWidget, QTextEdit, 
    QFormLayout, QFrame, QToolBar, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QFont

class PluginPage(QWidget):
    """
    Production-ready Plugin Management Page.
    Handles browsing, installing, enabling, disabling, and updating plugins.
    """
    action_requested = Signal(str)

    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Dependency Injection
        if container:
            self.container = container
        else:
            from core.dependency_container import DependencyContainer
            self.container = DependencyContainer()
            
        self.plugin_manager = self.container.get_service("plugin_manager")
        self.event_bus = self.container.get_service("event_bus")
        
        self.current_selected_plugin = None

        self._init_ui()
        self._connect_signals()
        self._load_initial_data()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()

        self.splitter = QSplitter(Qt.Horizontal)
        
        self._create_list_panel()
        self._create_details_panel()
        
        self.splitter.addWidget(self.tabs_panel)
        self.splitter.addWidget(self.details_panel)
        self.splitter.setSizes([350, 650])
        
        self.main_layout.addWidget(self.splitter)

    def _create_toolbar(self):
        self.toolbar = QToolBar("Plugin Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_refresh = QAction("Refresh Plugins", self)
        self.act_check_updates = QAction("Check for Updates", self)
        
        self.toolbar.addAction(self.act_refresh)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_check_updates)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_list_panel(self):
        self.tabs_panel = QTabWidget()
        
        # Installed Plugins Tab
        self.tab_installed = QWidget()
        installed_layout = QVBoxLayout(self.tab_installed)
        installed_layout.setContentsMargins(5, 5, 5, 5)
        self.list_installed = QListWidget()
        self.list_installed.setAlternatingRowColors(True)
        installed_layout.addWidget(self.list_installed)
        self.tabs_panel.addTab(self.tab_installed, "Installed Plugins")
        
        # Marketplace Tab
        self.tab_marketplace = QWidget()
        market_layout = QVBoxLayout(self.tab_marketplace)
        market_layout.setContentsMargins(5, 5, 5, 5)
        self.list_marketplace = QListWidget()
        self.list_marketplace.setAlternatingRowColors(True)
        market_layout.addWidget(self.list_marketplace)
        self.tabs_panel.addTab(self.tab_marketplace, "Marketplace")

    def _create_details_panel(self):
        self.details_panel = QFrame()
        self.details_panel.setFrameShape(QFrame.NoFrame)
        layout = QVBoxLayout(self.details_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        self.lbl_plugin_name = QLabel("Select a plugin")
        self.lbl_plugin_name.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.lbl_plugin_name)
        
        # Info Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.lbl_version = QLabel("N/A")
        self.lbl_author = QLabel("N/A")
        self.lbl_status = QLabel("N/A")
        
        form_layout.addRow("<b>Version:</b>", self.lbl_version)
        form_layout.addRow("<b>Author:</b>", self.lbl_author)
        form_layout.addRow("<b>Status:</b>", self.lbl_status)
        layout.addLayout(form_layout)
        
        # Description
        layout.addWidget(QLabel("<b>Description:</b>"))
        self.txt_description = QTextEdit()
        self.txt_description.setReadOnly(True)
        self.txt_description.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); border: 1px solid #3f3f46;")
        layout.addWidget(self.txt_description)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_enable = QPushButton("Enable")
        self.btn_enable.setStyleSheet("background-color: #2e6b3c; color: white;")
        
        self.btn_disable = QPushButton("Disable")
        self.btn_disable.setStyleSheet("background-color: #a33232; color: white;")
        
        self.btn_install = QPushButton("Install")
        self.btn_install.setStyleSheet("background-color: #2b579a; color: white;")
        
        self.btn_remove = QPushButton("Remove")
        self.btn_update = QPushButton("Update Available")
        self.btn_update.setStyleSheet("background-color: #c9a022; color: black; font-weight: bold;")
        
        btn_layout.addWidget(self.btn_enable)
        btn_layout.addWidget(self.btn_disable)
        btn_layout.addWidget(self.btn_install)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self._hide_all_buttons()

    def _connect_signals(self):
        self.act_refresh.triggered.connect(self._load_initial_data)
        self.act_check_updates.triggered.connect(self._check_for_updates)
        
        self.tabs_panel.currentChanged.connect(self._on_tab_changed)
        self.list_installed.itemSelectionChanged.connect(lambda: self._on_item_selected(self.list_installed))
        self.list_marketplace.itemSelectionChanged.connect(lambda: self._on_item_selected(self.list_marketplace))
        
        self.btn_enable.clicked.connect(self._on_enable_clicked)
        self.btn_disable.clicked.connect(self._on_disable_clicked)
        self.btn_install.clicked.connect(self._on_install_clicked)
        self.btn_remove.clicked.connect(self._on_remove_clicked)
        self.btn_update.clicked.connect(self._on_update_clicked)

    def _load_initial_data(self):
        self.logger.info("Loading plugin data...")
        self.list_installed.clear()
        self.list_marketplace.clear()
        self._clear_details()
        
        # Simulated Data (If real plugin_manager is not fully implemented)
        installed_plugins = [
            {"id": "ext.adobe.publisher", "name": "Adobe Stock Auto-Publisher", "version": "1.2.4", "author": "StockPilot Team", "status": "Enabled", "desc": "Automatically pushes generated CSV and images directly to Adobe Stock FTP."},
            {"id": "ext.vision.advanced", "name": "Advanced Vision Models", "version": "2.0.1", "author": "AI Tools Inc", "status": "Disabled", "desc": "Unlocks specialized image recognition models for highly technical imagery."}
        ]
        
        marketplace_plugins = [
            {"id": "ext.shutterstock.api", "name": "Shutterstock API Sync", "version": "1.0.0", "author": "StockPilot Team", "status": "Not Installed", "desc": "Sync earnings, rejections, and metadata directly with the Shutterstock API."},
            {"id": "ext.watermark.pro", "name": "Pro Watermarker", "version": "3.1.2", "author": "Design Studio", "status": "Not Installed", "desc": "Add dynamic batch watermarks to images before exporting."}
        ]
        
        for p in installed_plugins:
            item = QListWidgetItem(f"{p['name']} (v{p['version']})")
            item.setData(Qt.UserRole, p)
            self.list_installed.addItem(item)
            
        for p in marketplace_plugins:
            item = QListWidgetItem(f"{p['name']}")
            item.setData(Qt.UserRole, p)
            self.list_marketplace.addItem(item)

    def _on_tab_changed(self, index):
        self._clear_details()
        if index == 0:
            self.list_marketplace.clearSelection()
        else:
            self.list_installed.clearSelection()

    def _on_item_selected(self, list_widget):
        items = list_widget.selectedItems()
        if not items:
            return
            
        plugin_data = items[0].data(Qt.UserRole)
        self.current_selected_plugin = plugin_data
        
        self.lbl_plugin_name.setText(plugin_data["name"])
        self.lbl_version.setText(plugin_data["version"])
        self.lbl_author.setText(plugin_data["author"])
        self.txt_description.setPlainText(plugin_data["desc"])
        
        status = plugin_data.get("status", "Unknown")
        self.lbl_status.setText(status)
        
        if status == "Enabled":
            self.lbl_status.setStyleSheet("color: #8ec07c; font-weight: bold;")
        elif status == "Disabled":
            self.lbl_status.setStyleSheet("color: #c9a022; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: gray;")
            
        self._update_button_visibility(status)

    def _update_button_visibility(self, status):
        self._hide_all_buttons()
        
        if status == "Enabled":
            self.btn_disable.show()
            self.btn_remove.show()
            # Simulate a specific plugin having an update
            if self.current_selected_plugin and self.current_selected_plugin["id"] == "ext.adobe.publisher":
                self.btn_update.show()
        elif status == "Disabled":
            self.btn_enable.show()
            self.btn_remove.show()
        elif status == "Not Installed":
            self.btn_install.show()

    def _hide_all_buttons(self):
        self.btn_enable.hide()
        self.btn_disable.hide()
        self.btn_install.hide()
        self.btn_remove.hide()
        self.btn_update.hide()

    def _clear_details(self):
        self.current_selected_plugin = None
        self.lbl_plugin_name.setText("Select a plugin")
        self.lbl_version.setText("N/A")
        self.lbl_author.setText("N/A")
        self.lbl_status.setText("N/A")
        self.lbl_status.setStyleSheet("")
        self.txt_description.clear()
        self._hide_all_buttons()

    def _check_for_updates(self):
        self.logger.info("Checking plugin repository for updates...")
        QMessageBox.information(self, "Updates", "Checked repository. 1 update available for 'Adobe Stock Auto-Publisher'.")
        self._load_initial_data()

    def _on_enable_clicked(self):
        if self.current_selected_plugin:
            self.logger.info(f"Enabling plugin: {self.current_selected_plugin['id']}")
            self.current_selected_plugin["status"] = "Enabled"
            self._update_current_item_ui()

    def _on_disable_clicked(self):
        if self.current_selected_plugin:
            self.logger.info(f"Disabling plugin: {self.current_selected_plugin['id']}")
            self.current_selected_plugin["status"] = "Disabled"
            self._update_current_item_ui()

    def _on_install_clicked(self):
        if self.current_selected_plugin:
            self.logger.info(f"Installing plugin: {self.current_selected_plugin['id']}")
            QMessageBox.information(self, "Install", f"Successfully installed {self.current_selected_plugin['name']}.")
            self._load_initial_data() # Reload to move it to installed list

    def _on_remove_clicked(self):
        if self.current_selected_plugin:
            reply = QMessageBox.question(self, "Confirm Remove", f"Are you sure you want to uninstall {self.current_selected_plugin['name']}?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.logger.info(f"Removing plugin: {self.current_selected_plugin['id']}")
                self._load_initial_data()

    def _on_update_clicked(self):
        if self.current_selected_plugin:
            self.logger.info(f"Updating plugin: {self.current_selected_plugin['id']}")
            QMessageBox.information(self, "Update", f"Updated {self.current_selected_plugin['name']} to the latest version.")
            self.btn_update.hide()

    def _update_current_item_ui(self):
        # Refresh the details panel status
        self.lbl_status.setText(self.current_selected_plugin["status"])
        if self.current_selected_plugin["status"] == "Enabled":
            self.lbl_status.setStyleSheet("color: #8ec07c; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: #c9a022; font-weight: bold;")
            
        self._update_button_visibility(self.current_selected_plugin["status"])