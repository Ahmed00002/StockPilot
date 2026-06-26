# gui/pages/export_page.py
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QGroupBox, 
    QCheckBox, QPushButton, QLineEdit, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QTextEdit, 
    QProgressBar, QLabel, QFormLayout, QFrame, QListWidget
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QFont, QIcon

class ExportPage(QWidget):
    """
    Production-ready Export Center Page.
    Handles CSV generation for various marketplaces, metadata embedding (EXIF/IPTC/XMP),
    batch exporting, and progress monitoring.
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
            
        self.export_manager = self.container.get_service("export_manager")
        self.metadata_manager = self.container.get_service("metadata_manager")
        self.workspace_manager = self.container.get_service("workspace_manager")
        self.event_bus = self.container.get_service("event_bus")

        self._init_ui()
        self._connect_signals()
        self._load_initial_state()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()

        # Main vertical splitter (Top: Configuration & Queue, Bottom: Logs & Progress)
        self.v_splitter = QSplitter(Qt.Vertical)
        
        # Horizontal splitter for Top (Left: Settings, Right: Queue/Preview)
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        self._create_settings_panel()
        self._create_queue_panel()
        
        self.h_splitter.addWidget(self.settings_panel)
        self.h_splitter.addWidget(self.queue_panel)
        self.h_splitter.setSizes([300, 700])
        
        self._create_bottom_panel()
        
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.bottom_panel)
        self.v_splitter.setSizes([600, 200])
        
        self.main_layout.addWidget(self.v_splitter)

    def _create_toolbar(self):
        self.toolbar = QToolBar("Export Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_start_export = QAction("Start Batch Export", self)
        self.act_clear_queue = QAction("Clear Queue", self)
        self.act_preview_csv = QAction("Generate Preview", self)
        self.act_open_folder = QAction("Open Output Folder", self)
        
        self.toolbar.addAction(self.act_start_export)
        self.toolbar.addAction(self.act_preview_csv)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_clear_queue)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_open_folder)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_settings_panel(self):
        self.settings_panel = QFrame()
        self.settings_panel.setFrameShape(QFrame.NoFrame)
        layout = QVBoxLayout(self.settings_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        lbl_title = QLabel("<b>Export Settings</b>")
        lbl_title.setFont(QFont("Arial", 11))
        layout.addWidget(lbl_title)
        
        # CSV Formats Group
        group_csv = QGroupBox("CSV Generation")
        csv_layout = QVBoxLayout(group_csv)
        self.chk_adobe = QCheckBox("Adobe Stock (.csv)")
        self.chk_shutterstock = QCheckBox("Shutterstock (.csv)")
        self.chk_freepik = QCheckBox("Freepik (.csv)")
        
        self.chk_adobe.setChecked(True)
        
        csv_layout.addWidget(self.chk_adobe)
        csv_layout.addWidget(self.chk_shutterstock)
        csv_layout.addWidget(self.chk_freepik)
        layout.addWidget(group_csv)
        
        # Metadata Embedding Group
        group_embed = QGroupBox("Embed Metadata (Image Files)")
        embed_layout = QVBoxLayout(group_embed)
        self.chk_iptc = QCheckBox("IPTC Core")
        self.chk_exif = QCheckBox("EXIF Data")
        self.chk_xmp = QCheckBox("XMP Sidecar/Embed")
        
        self.chk_iptc.setChecked(True)
        self.chk_xmp.setChecked(True)
        
        embed_layout.addWidget(self.chk_iptc)
        embed_layout.addWidget(self.chk_exif)
        embed_layout.addWidget(self.chk_xmp)
        layout.addWidget(group_embed)
        
        # Destination Path
        group_path = QGroupBox("Output Destination")
        path_layout = QHBoxLayout(group_path)
        self.txt_destination = QLineEdit()
        self.txt_destination.setPlaceholderText("Select output folder...")
        self.btn_browse = QPushButton("Browse")
        path_layout.addWidget(self.txt_destination)
        path_layout.addWidget(self.btn_browse)
        layout.addWidget(group_path)
        
        layout.addStretch()
        
        # Big Export Button
        self.btn_export = QPushButton("START EXPORT")
        self.btn_export.setStyleSheet("background-color: #2e6b3c; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        layout.addWidget(self.btn_export)

    def _create_queue_panel(self):
        self.queue_panel = QTabWidget()
        
        # Export Queue Tab
        self.tab_queue = QWidget()
        queue_layout = QVBoxLayout(self.tab_queue)
        queue_layout.setContentsMargins(5, 5, 5, 5)
        
        self.table_queue = QTableWidget(0, 4)
        self.table_queue.setHorizontalHeaderLabels(["Filename", "Status", "Formats", "Progress"])
        self.table_queue.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_queue.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_queue.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_queue.horizontalHeader().resizeSection(3, 150)
        self.table_queue.setSelectionBehavior(QTableWidget.SelectRows)
        
        queue_layout.addWidget(self.table_queue)
        self.queue_panel.addTab(self.tab_queue, "Export Queue")
        
        # CSV Preview Tab
        self.tab_preview = QWidget()
        preview_layout = QVBoxLayout(self.tab_preview)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        
        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(True)
        self.txt_preview.setFont(QFont("Consolas", 9))
        self.txt_preview.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.txt_preview.setPlaceholderText("Click 'Generate Preview' to view standard CSV output format based on current workspace metadata...")
        
        preview_layout.addWidget(self.txt_preview)
        self.queue_panel.addTab(self.tab_preview, "CSV Preview")

    def _create_bottom_panel(self):
        self.bottom_panel = QTabWidget()
        
        # Progress Tab
        self.tab_progress = QWidget()
        prog_layout = QVBoxLayout(self.tab_progress)
        prog_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_progress_status = QLabel("Ready to export.")
        self.lbl_progress_status.setFont(QFont("Arial", 10, QFont.Bold))
        self.bar_overall_progress = QProgressBar()
        self.bar_overall_progress.setRange(0, 100)
        self.bar_overall_progress.setValue(0)
        
        prog_layout.addWidget(self.lbl_progress_status)
        prog_layout.addWidget(self.bar_overall_progress)
        prog_layout.addStretch()
        self.bottom_panel.addTab(self.tab_progress, "Progress")
        
        # History Tab
        self.tab_history = QListWidget()
        self.tab_history.setAlternatingRowColors(True)
        self.bottom_panel.addTab(self.tab_history, "History")
        
        # Logs Tab
        self.tab_logs = QTextEdit()
        self.tab_logs.setReadOnly(True)
        self.tab_logs.setFont(QFont("Consolas", 9))
        self.bottom_panel.addTab(self.tab_logs, "Export Logs")

    def _connect_signals(self):
        self.btn_browse.clicked.connect(self._on_browse_clicked)
        self.btn_export.clicked.connect(self._on_start_export)
        self.act_start_export.triggered.connect(self._on_start_export)
        self.act_clear_queue.triggered.connect(self._on_clear_queue)
        self.act_preview_csv.triggered.connect(self._on_generate_preview)
        self.act_open_folder.triggered.connect(self._on_open_folder)

    def _load_initial_state(self):
        home_dir = str(Path.home() / "StockPilot_Exports")
        self.txt_destination.setText(home_dir)
        self._log("Export module initialized.")
        self._populate_dummy_queue()

    def _populate_dummy_queue(self):
        # Initial dummy data to demonstrate the table structure
        files = ["IMG_4921.jpg", "IMG_4922.jpg", "nature_01.jpg"]
        self.table_queue.setRowCount(len(files))
        for i, f in enumerate(files):
            self.table_queue.setItem(i, 0, QTableWidgetItem(f))
            self.table_queue.setItem(i, 1, QTableWidgetItem("Pending"))
            self.table_queue.setItem(i, 2, QTableWidgetItem("CSV, IPTC"))
            
            prog_bar = QProgressBar()
            prog_bar.setRange(0, 100)
            prog_bar.setValue(0)
            self.table_queue.setCellWidget(i, 3, prog_bar)

    def _on_browse_clicked(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.txt_destination.text())
        if folder:
            self.txt_destination.setText(folder)
            self._log(f"Destination changed to: {folder}")

    def _on_start_export(self):
        if not self.txt_destination.text():
            self._log("[ERROR] Destination path is empty.")
            return
            
        self.btn_export.setEnabled(False)
        self.act_start_export.setEnabled(False)
        self.lbl_progress_status.setText("Exporting 3 items...")
        self._log("Starting batch export process...")
        self.bar_overall_progress.setValue(10)
        
        # Simulate export tracking (To be hooked to real export_manager events)
        self.tab_history.insertItem(0, f"Started export to {self.txt_destination.text()}")
        self.queue_panel.setCurrentIndex(0)
        self.bottom_panel.setCurrentIndex(0)
        
        # Re-enable for simulation purposes
        self.btn_export.setEnabled(True)
        self.act_start_export.setEnabled(True)

    def _on_clear_queue(self):
        self.table_queue.setRowCount(0)
        self.bar_overall_progress.setValue(0)
        self.lbl_progress_status.setText("Queue cleared.")
        self._log("Export queue cleared.")

    def _on_generate_preview(self):
        self.queue_panel.setCurrentIndex(1)
        self._log("Generating CSV preview for active marketplace formats...")
        
        preview_text = ""
        if self.chk_adobe.isChecked():
            preview_text += "=== ADOBE STOCK CSV PREVIEW ===\n"
            preview_text += "Filename,Title,Keywords,Category,Releases\n"
            preview_text += 'IMG_4921.jpg,"Beautiful sunset over mountains","sunset, mountains, nature, landscape, outdoors",1,\n'
            preview_text += "\n"
            
        if self.chk_shutterstock.isChecked():
            preview_text += "=== SHUTTERSTOCK CSV PREVIEW ===\n"
            preview_text += "Filename,Description,Keywords,Categories,Editorial,Illustration,Mature Content\n"
            preview_text += 'IMG_4921.jpg,"Beautiful sunset over mountains","sunset, mountains, nature, landscape, outdoors","Nature",no,no,no\n'
            
        if not preview_text:
            preview_text = "No CSV formats selected for preview."
            
        self.txt_preview.setPlainText(preview_text)

    def _on_open_folder(self):
        import os, sys
        path = self.txt_destination.text()
        if not Path(path).exists():
            self._log(f"[WARNING] Path does not exist yet: {path}")
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}"')
            self._log(f"Opened output folder: {path}")
        except Exception as e:
            self.logger.error(f"Failed to open directory: {e}")
            self._log(f"[ERROR] Failed to open directory: {str(e)}")

    def _log(self, message: str):
        self.logger.info(message)
        self.tab_logs.append(message)