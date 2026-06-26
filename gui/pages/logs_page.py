# gui/pages/logs_page.py
import logging
import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QToolBar, QLineEdit, QCheckBox, QPushButton, 
    QFileDialog, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QAction, QFont, QColor

class LogsPage(QWidget):
    """
    Production-ready Application Logs Page.
    Monitors, filters, and displays application logs in real-time.
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
            
        self.event_bus = self.container.get_service("event_bus")
        
        # Log File Configuration
        self.log_file_path = Path("logs/app.log")
        self._last_position = 0
        self._max_rows = 5000
        
        # Regex for standard log format: 2026-06-27 02:01:13,622 [INFO] module: message
        self.log_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})\s+\[([A-Z]+)\]\s+(.*?):\s+(.*)$")

        self._init_ui()
        self._connect_signals()
        self._setup_auto_refresh()
        self._load_initial_logs()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._create_toolbar()
        self._create_filters_bar()
        self._create_log_table()

    def _create_toolbar(self):
        self.toolbar = QToolBar("Logs Toolbar", self)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(16, 16))
        
        self.act_export = QAction("Export Logs", self)
        self.act_clear = QAction("Clear Logs", self)
        
        self.toolbar.addAction(self.act_export)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_clear)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().Policy.Expanding, spacer.sizePolicy().Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Auto Refresh Toggle
        self.chk_auto_refresh = QCheckBox("Auto Refresh")
        self.chk_auto_refresh.setChecked(True)
        self.chk_auto_refresh.setStyleSheet("margin-right: 15px; font-weight: bold;")
        self.toolbar.addWidget(self.chk_auto_refresh)
        
        self.main_layout.addWidget(self.toolbar)

    def _create_filters_bar(self):
        self.filters_frame = QFrame()
        self.filters_frame.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.05); border-bottom: 1px solid #3f3f46; }")
        
        layout = QHBoxLayout(self.filters_frame)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("<b>Filter:</b>"))
        
        self.chk_error = QCheckBox("Errors")
        self.chk_error.setChecked(True)
        self.chk_error.setStyleSheet("color: #ff6b6b;")
        
        self.chk_warn = QCheckBox("Warnings")
        self.chk_warn.setChecked(True)
        self.chk_warn.setStyleSheet("color: #c9a022;")
        
        self.chk_info = QCheckBox("Info")
        self.chk_info.setChecked(True)
        self.chk_info.setStyleSheet("color: #8ec07c;")
        
        self.chk_debug = QCheckBox("Debug")
        self.chk_debug.setChecked(True)
        self.chk_debug.setStyleSheet("color: #888888;")
        
        layout.addWidget(self.chk_error)
        layout.addWidget(self.chk_warn)
        layout.addWidget(self.chk_info)
        layout.addWidget(self.chk_debug)
        
        layout.addSpacing(20)
        
        # Search Box
        layout.addWidget(QLabel("<b>Search:</b>"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search messages or modules...")
        self.txt_search.setMinimumWidth(300)
        layout.addWidget(self.txt_search)
        
        layout.addStretch()
        self.main_layout.addWidget(self.filters_frame)

    def _create_log_table(self):
        self.table_logs = QTableWidget(0, 4)
        self.table_logs.setHorizontalHeaderLabels(["Timestamp", "Level", "Module", "Message"])
        self.table_logs.verticalHeader().setVisible(False)
        self.table_logs.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_logs.setAlternatingRowColors(True)
        self.table_logs.setShowGrid(False)
        self.table_logs.setFont(QFont("Consolas", 9))
        
        header = self.table_logs.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.main_layout.addWidget(self.table_logs)

    def _connect_signals(self):
        self.act_export.triggered.connect(self._export_logs)
        self.act_clear.triggered.connect(self._clear_logs)
        self.chk_auto_refresh.stateChanged.connect(self._toggle_auto_refresh)
        
        # Debounced search filter
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._apply_filters)
        self.txt_search.textChanged.connect(lambda: self.search_timer.start(300))
        
        # Checkbox filters
        self.chk_error.stateChanged.connect(self._apply_filters)
        self.chk_warn.stateChanged.connect(self._apply_filters)
        self.chk_info.stateChanged.connect(self._apply_filters)
        self.chk_debug.stateChanged.connect(self._apply_filters)

    def _setup_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._read_new_logs)
        self.refresh_timer.start(2000)

    def _toggle_auto_refresh(self):
        if self.chk_auto_refresh.isChecked():
            self.refresh_timer.start(2000)
            self._read_new_logs()
        else:
            self.refresh_timer.stop()

    def _load_initial_logs(self):
        if not self.log_file_path.exists():
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_file_path.touch()
        
        self.table_logs.setRowCount(0)
        self._last_position = 0
        self._read_new_logs()

    def _read_new_logs(self):
        if not self.log_file_path.exists():
            return
            
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(self._last_position)
                new_lines = f.readlines()
                self._last_position = f.tell()
                
            if not new_lines:
                return
                
            self.table_logs.setUpdatesEnabled(False)
            
            for line in new_lines:
                line = line.rstrip('\n')
                if not line:
                    continue
                    
                match = self.log_pattern.match(line)
                if match:
                    timestamp, level, module, message = match.groups()
                    self._add_log_entry(timestamp, level, module, message)
                else:
                    # Append to previous multiline log (e.g., tracebacks)
                    row = self.table_logs.rowCount() - 1
                    if row >= 0:
                        msg_item = self.table_logs.item(row, 3)
                        msg_item.setText(msg_item.text() + "\n" + line)
            
            self._enforce_max_rows()
            self._apply_filters()
            
            # Auto scroll to bottom if auto-refresh is on
            if self.chk_auto_refresh.isChecked():
                self.table_logs.scrollToBottom()
                
            self.table_logs.setUpdatesEnabled(True)
            
        except Exception as e:
            self.logger.error(f"Error reading logs: {e}")

    def _add_log_entry(self, timestamp: str, level: str, module: str, message: str):
        row = self.table_logs.rowCount()
        self.table_logs.insertRow(row)
        
        item_time = QTableWidgetItem(timestamp)
        item_level = QTableWidgetItem(level)
        item_module = QTableWidgetItem(module)
        item_message = QTableWidgetItem(message)
        
        # Styling
        font_bold = QFont("Consolas", 9, QFont.Bold)
        item_level.setFont(font_bold)
        
        if level == "ERROR":
            item_level.setForeground(QColor("#ff6b6b"))
        elif level == "WARNING":
            item_level.setForeground(QColor("#c9a022"))
        elif level == "INFO":
            item_level.setForeground(QColor("#8ec07c"))
        elif level == "DEBUG":
            item_level.setForeground(QColor("#888888"))
            
        # Prevent editing
        for item in (item_time, item_level, item_module, item_message):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            
        self.table_logs.setItem(row, 0, item_time)
        self.table_logs.setItem(row, 1, item_level)
        self.table_logs.setItem(row, 2, item_module)
        self.table_logs.setItem(row, 3, item_message)

    def _enforce_max_rows(self):
        while self.table_logs.rowCount() > self._max_rows:
            self.table_logs.removeRow(0)

    def _apply_filters(self):
        search_term = self.txt_search.text().lower().strip()
        show_err = self.chk_error.isChecked()
        show_warn = self.chk_warn.isChecked()
        show_info = self.chk_info.isChecked()
        show_dbg = self.chk_debug.isChecked()
        
        for row in range(self.table_logs.rowCount()):
            level_item = self.table_logs.item(row, 1)
            msg_item = self.table_logs.item(row, 3)
            mod_item = self.table_logs.item(row, 2)
            
            if not level_item: 
                continue
                
            level = level_item.text()
            
            # Filter by Level
            hidden_by_level = False
            if level == "ERROR" and not show_err: hidden_by_level = True
            elif level == "WARNING" and not show_warn: hidden_by_level = True
            elif level == "INFO" and not show_info: hidden_by_level = True
            elif level == "DEBUG" and not show_dbg: hidden_by_level = True
            
            if hidden_by_level:
                self.table_logs.setRowHidden(row, True)
                continue
                
            # Filter by Search String
            if search_term:
                msg_text = msg_item.text().lower()
                mod_text = mod_item.text().lower()
                if search_term not in msg_text and search_term not in mod_text:
                    self.table_logs.setRowHidden(row, True)
                    continue
                    
            self.table_logs.setRowHidden(row, False)

    def _export_logs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Application Logs", "", "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                import shutil
                shutil.copy2(self.log_file_path, path)
                QMessageBox.information(self, "Export Successful", f"Logs exported to:\n{path}")
            except Exception as e:
                self.logger.error(f"Failed to export logs: {e}")
                QMessageBox.critical(self, "Export Failed", f"An error occurred while exporting logs:\n{e}")

    def _clear_logs(self):
        reply = QMessageBox.question(
            self, "Clear Logs", "Are you sure you want to permanently clear the application log file?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                with open(self.log_file_path, 'w') as f:
                    f.truncate(0)
                self.table_logs.setRowCount(0)
                self._last_position = 0
                self.logger.info("Application logs cleared by user.")
                self._read_new_logs() # Load the clearance log
            except Exception as e:
                self.logger.error(f"Failed to clear log file: {e}")
                QMessageBox.critical(self, "Error", f"Failed to clear log file:\n{e}")